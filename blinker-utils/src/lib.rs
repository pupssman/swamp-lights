#![cfg_attr(not(test), no_std)]

use smart_leds::{RGB8};

#[derive(Clone, Copy)]
pub struct SingleGradientPulser {
    pub start: RGB8,
    pub end: RGB8,
    pub period: u8, // in clicks
    pub current: u8
}

impl SingleGradientPulser {
    pub fn pulse(&mut self, length: u8) -> SingleColorIterator {
        if self.current >= self.period {
            self.current = 0;
        } else {
            self.current += 1;
        }

        let frac: f32 = self.current as f32 / self.period as f32;
        let rb = (self.end.r as f32 - self.start.r as f32) * frac;
        
        SingleColorIterator {
            color: RGB8 {
                // FIXME: overflows!
                r: rb as u8 + self.start.r, 
                g: (self.end.g - self.start.g) * self.current / self.period + self.start.g, 
                b: (self.end.b - self.start.b) * self.current / self.period + self.start.b, 
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

#[derive(Clone, Copy)]
pub struct GradientPulserBulb {
    pub length: u8,
    pub current: u8,
    pub sgps: [Option<SingleGradientPulser>; 4]  // at most 4 gradients, duh
}

#[derive(Clone, Copy)]
pub struct GradientPulserChain {
    pub gpbs: [Option<GradientPulserBulb>; 10],  // at most 10 bulbs, duh
    pub delay_ms: u16
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
}
