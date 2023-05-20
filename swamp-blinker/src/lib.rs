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
    pub ws: Ws2812<Spi>,
    pub buf: [RGB8;100]
}

impl RgbWritable for WsWriter {
    // we need to pass everything into a buf first so it actually runs smoothly
    fn write(&mut self, leds: impl Iterator<Item = RGB8>) {
        for (i, l) in leds.enumerate() { 
            //print!("({} {} {})", l.r, l.g, l.b); 
            self.buf[i] = l
        } 
        // println!("//");
        match self.ws.write(self.buf.into_iter()) {
            Ok(_) => (),
            Err(_) => {
                println!("write error");
            }
        }
    }
}
