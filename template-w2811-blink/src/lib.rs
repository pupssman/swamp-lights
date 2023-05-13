#![no_std]
use core::iter::Iterator;
use core::option::Option;
use core::option::Option::None;
use arduino_hal::Spi;
use arduino_hal::Usart;
use arduino_hal::prelude::*;
use smart_leds::{RGB8};

use ws2812_spi as ws2812;
use crate::ws2812::Ws2812;
use smart_leds::{SmartLedsWrite};


#[derive(Clone, Copy)]
pub struct SingleGradientPulser {
    pub start: RGB8,
    pub end: RGB8,
    pub period: u8, // in clicks
    pub current: u8
}

impl SingleGradientPulser {
    fn pulse(&mut self, length: u8) -> SingleColorIterator {
        if self.current >= self.period {
            self.current = 0;
        } else {
            self.current += 1;
        }
        
        SingleColorIterator {
            color: RGB8 {
                // FIXME: overflows!
                r: (self.end.r - self.start.r) * self.current / self.period + self.start.r, 
                g: (self.end.g - self.start.g) * self.current / self.period + self.start.g, 
                b: (self.end.b - self.start.b) * self.current / self.period + self.start.b, 
            },
            index: length
        }
    }
}

struct SingleColorIterator {
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

pub fn pulse_once(chain: &GradientPulserChain, ws: &mut Ws2812<Spi>) {
    for maybe_bulb in chain.gpbs {
        match maybe_bulb {
            None => (),
            Some(bulb) => {
                let maybe_pulser = bulb.sgps[0];  // FIXME: should use different ones)
                match maybe_pulser {
                    Some(mut pulser) => {
                        match ws.write(pulser.pulse(bulb.length)) {
                            Ok(_) => (),
                            Err(_) => {}
                        }
                    }, None => ()
                }
            }
        }
    }
}
