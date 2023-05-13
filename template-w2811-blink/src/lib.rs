#![no_std]

extern crate alloc;

use alloc::boxed::Box;
use core::iter::{Iterator, IntoIterator};
use core::option::Option;
use core::option::Option::None;

use smart_leds::{RGB8};
use ws2812_spi as ws2812;
use crate::ws2812::Ws2812;

pub const TOTAL_LEDS: usize= 300;

pub trait TickedLight {
    fn on_tick(&self, tick: i16) -> Box<dyn Iterator<Item = RGB8>>;
}

pub struct WsTicker<'a, SPI> {
    pub ws: &'a Ws2812<SPI>,
    pub ticked: &'a dyn TickedLight,
    pub period_ms: u16,
}

#[derive(Clone, Copy)]
pub struct SingleColorLine {
    pub r: u8,
    pub g: u8,
    pub b: u8
}

impl TickedLight for SingleColorLine {
    // just return same color
    fn on_tick(&self, tick: i16) -> Box<dyn Iterator<Item = RGB8>>{
        return self.into_iter();
    }
}

#[derive(Clone, Copy)]
pub struct SingleColorLineIterator {
    scl: SingleColorLine,
    index: usize
}

impl IntoIterator for SingleColorLine {
    type Item = RGB8;
    type IntoIter = SingleColorLineIterator;
    
    fn into_iter(self) -> SingleColorLineIterator {
        SingleColorLineIterator {
            scl: self,
            index: TOTAL_LEDS
        }
    }
}

impl Iterator for SingleColorLineIterator {
    type Item = RGB8;
    fn next(&mut self) -> Option<Self::Item> {
        if self.index > 0 {
            self.index -= 1;
            return Some(RGB8{
                r: self.scl.r,
                g: self.scl.g,
                b: self.scl.b
            })
        } else {
            return None

        }    
    } 
}

#[cfg(test)]
mod tests {
    #[test]
    fn iter_smoke() {
        assert_eq!(2, 2)
    }
}