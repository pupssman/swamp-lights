#![no_std]
use arduino_hal::Spi;

use ws2812_spi as ws2812;
use crate::ws2812::Ws2812;
use smart_leds::{SmartLedsWrite, RGB8};

use blinker_utils::*;  // sister-crate, go with all-imports

pub struct WsWriter {
    pub ws: Ws2812<Spi>
}

impl RgbWritable for WsWriter {
    fn write(&mut self, leds: impl Iterator<Item = RGB8>) {
        match self.ws.write(leds) {
            Ok(_) => (),
            Err(_) => {
                // FIXME: log error or restart!
            }
        }
    }
}
