#![no_std]
use arduino_hal::Spi;

use ws2812_spi as ws2812;
use crate::ws2812::Ws2812;
use smart_leds::{SmartLedsWrite, RGB8};

use blinker_utils::*;  // sister-crate, go with all-imports


use panic_halt as _;

use avr_device::interrupt;
use core::cell::RefCell;

type Console = arduino_hal::hal::usart::Usart0<arduino_hal::DefaultClock>;
pub static CONSOLE: interrupt::Mutex<RefCell<Option<Console>>> =
    interrupt::Mutex::new(RefCell::new(None));

#[macro_export]
macro_rules! print {
    ($($t:tt)*) => {
        interrupt::free(
            |cs| {
                if let Some(console) = CONSOLE.borrow(cs).borrow_mut().as_mut() {
                    let _ = ufmt::uwrite!(console, $($t)*);
                }
            },
        )
    };
}

#[macro_export]
macro_rules! println {
    ($($t:tt)*) => {
        interrupt::free(
            |cs| {
                if let Some(console) = CONSOLE.borrow(cs).borrow_mut().as_mut() {
                    let _ = ufmt::uwriteln!(console, $($t)*);
                }
            },
        )
    };
}

pub fn put_console(console: Console) {
    interrupt::free(|cs| {
        *CONSOLE.borrow(cs).borrow_mut() = Some(console);
    })
}


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
