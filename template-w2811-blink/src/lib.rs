#![no_std]
use core::iter::{Iterator, IntoIterator};
use core::option::Option;
use core::option::Option::None;
use smart_leds::{RGB8};

pub const TOTAL_LEDS: usize= 150;

#[derive(Clone, Copy)]
pub struct SingleColorLine {
    pub r: u8,
    pub g: u8,
    pub b: u8
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