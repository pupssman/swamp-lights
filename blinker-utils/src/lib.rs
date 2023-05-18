#![cfg_attr(not(test), no_std)]

use smart_leds::{RGB8};

pub struct SingleGradientPulser {
    pub start: RGB8,
    pub end: RGB8,
    pub period: u8, // in clicks
    pub current: u8
}

impl SingleGradientPulser {
    pub fn pulse(&mut self, length: u8) -> SingleColorIterator {
        let frac: f32 = self.current as f32 / self.period as f32;
        let rb = (self.end.r as f32 - self.start.r as f32) * frac;
        let gb = (self.end.g as f32 - self.start.g as f32) * frac;
        let bb = (self.end.b as f32 - self.start.b as f32) * frac;

        if self.current >= self.period {
            self.current = 0;
        } else {
            self.current += 1;
        }
        
        SingleColorIterator {
            color: RGB8 {
                // FIXME: overflows!
                r: (rb + self.start.r as f32) as u8, 
                g: (gb + self.start.g as f32) as u8, 
                b: (bb + self.start.b as f32) as u8, 
            },
            index: length
        }
    }
}

pub struct SingleColorIterator {
    color: RGB8,
    index: u8
}

impl Iterator for SingleColorIterator {
    type Item = RGB8;
    fn next(&mut self) -> Option<Self::Item> {
        if self.index > 0 {
            self.index -= 1;
            return Some(self.color)
        } else {
            return None
        }    
    } 
}

pub struct GradientPulserBulb {
    pub length: u8,
    pub current: u8,
    pub sgps: [Option<SingleGradientPulser>; 4]  // at most 4 gradients, duh
}

pub struct GradientPulserChain {
    pub gpbs: [Option<GradientPulserBulb>; 10],  // at most 10 bulbs, duh
    pub delay_ms: u16
}

pub trait RgbWritable {
    fn write(&mut self, leds: SingleColorIterator);
}

impl GradientPulserChain {
    pub fn pulse_once(&mut self, consumer: &mut dyn RgbWritable) {
        for maybe_bulb in &mut self.gpbs {
            match maybe_bulb {
                None => (),
                Some(ref mut bulb) => {
                    let maybe_pulser = &mut bulb.sgps[0];  // FIXME: should use different ones)
                    match maybe_pulser {
                        Some(ref mut pulser) => {
                            consumer.write(pulser.pulse(bulb.length));
                        }, None => ()
                    }
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = 2 + 2;
        assert_eq!(result, 4);
    }

    #[test]
    fn test_single_smokey() {
        let mut blinker = SingleGradientPulser {
            start: RGB8 {r:0, g:0, b:0},
            end: RGB8 {r:100, g:100, b:100},
            period: 10,
            current: 0    
        };

        // this takes out 0s
        blinker.pulse(1);
        let mut pulse = blinker.pulse(1);

        let first = pulse.next();
        assert!(first.is_some());
        assert_eq!(first.unwrap().r, 10);
        assert_eq!(first.unwrap().g, 10);
        assert_eq!(first.unwrap().b, 10);

        assert!(pulse.next().is_none());

        let mut pulse = blinker.pulse(1);

        let first = pulse.next();
        assert!(first.is_some());
        assert_eq!(first.unwrap().r, 20);
        assert_eq!(first.unwrap().g, 20);
        assert_eq!(first.unwrap().b, 20);

        assert!(pulse.next().is_none());
    }

    struct RgbAccumulator {
        leds: Vec<RGB8>
    }

    impl RgbWritable for RgbAccumulator {
        fn write(&mut self, leds: SingleColorIterator) {
            for led in leds {
                self.leds.push(led);
            }
        }
    }

    #[test]
    fn test_pulse_once() {
        let mut bulbs = [None, None, None, None, None, None, None, None, None, None];
    
        bulbs[0] = Some(GradientPulserBulb{
                length: 10,
                current: 0,
                sgps: [
                    Some(SingleGradientPulser{
                        start:smart_leds::RGB { r: 100, g: 100, b: 0},
                        end:smart_leds::RGB { r: 0, g: 0, b: 0},
                        period: 5,
                        current: 0
                    }), None, None, None
                ]
            });
    
        let mut chain = GradientPulserChain { 
            gpbs: bulbs,
            delay_ms: 100
        };

        let mut accumulator_1 = RgbAccumulator {leds: vec![]};
        let mut accumulator_2 = RgbAccumulator {leds: vec![]};

        chain.pulse_once(&mut accumulator_1);
        chain.pulse_once(&mut accumulator_2);

        assert_eq!(accumulator_1.leds[0], RGB8{r: 100, g: 100, b:0});
        assert_eq!(accumulator_1.leds[9], RGB8{r: 100, g: 100, b:0});

        assert_eq!(accumulator_2.leds[0], RGB8{r: 80, g: 80, b:0});
        assert_eq!(accumulator_2.leds[9], RGB8{r: 80, g: 80, b:0});
    }
}
