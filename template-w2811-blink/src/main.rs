#![no_std]
#![no_main]

use panic_halt as _;

use arduino_hal::prelude::*;
use arduino_hal::spi;

use ws2812_spi as ws2812;
use crate::ws2812::prerendered::Ws2812;
use smart_leds::{SmartLedsWrite, RGB8};

const TOTAL_LEDS: usize= 20;

#[arduino_hal::entry]
fn main() -> ! {
    let dp = arduino_hal::Peripherals::take().unwrap();
    let pins = arduino_hal::pins!(dp);

    // Create SPI interface.
    // We assign 4 well-known pins of SPI to our HW pins by numbers, see SPI docs
    let (spi, _) = spi::Spi::new(
        dp.SPI,
        pins.d13.into_output(),  // SCK pin -- clock
        pins.d11.into_output(),  // MOSI -- master-out-slave-in
        pins.d12.into_pull_up_input(),  // MISO --- master-in-slave-out -- that's whyt it's output!
        pins.d10.into_output(),  // SS -- slave select pin
        spi::Settings {
            clock: spi::SerialClockRate::OscfOver8,
            ..Default::default()
        },
    );

    let mut output_buffer = [0; 20 + (TOTAL_LEDS * 12)];
    let half_red: [RGB8; TOTAL_LEDS] = [RGB8 {r: 0, g: 0x77, b: 0}; TOTAL_LEDS];
    let all_red: [RGB8; TOTAL_LEDS] = [RGB8 {r: 0, g: 0xFF, b: 0}; TOTAL_LEDS];
    //let half_green: [RGB8; TOTAL_LEDS] = [RGB8 {r: 0, g: 0x77, b: 0}; TOTAL_LEDS];
    //let all_green: [RGB8; TOTAL_LEDS] = [RGB8 {r: 0, g: 0xFF, b: 0}; TOTAL_LEDS];
    let half_blue: [RGB8; TOTAL_LEDS] = [RGB8 {r: 0, g: 0, b: 0x77}; TOTAL_LEDS];
    let all_blue: [RGB8; TOTAL_LEDS] = [RGB8 {r: 0, g: 0, b: 0xFF}; TOTAL_LEDS];
    //let half_white: [RGB8; TOTAL_LEDS] = [RGB8 {r: 0x77, g: 0x77, b: 0x77}; TOTAL_LEDS];
    //let all_white: [RGB8; TOTAL_LEDS] = [RGB8 {r: 0xFF, g: 0xFF, b: 0xFF}; TOTAL_LEDS];
    let empty: [RGB8; TOTAL_LEDS] = [RGB8::default(); TOTAL_LEDS];

    let mut ws = Ws2812::new(spi, &mut output_buffer);

    // set up serial interface for text output
    let mut serial = arduino_hal::default_serial!(dp, pins, 57600);

    loop {
        ufmt::uwriteln!(&mut serial, "loop\r").void_unwrap();

        for layout in [
            half_red, all_red, empty, 
        //    half_blue, all_blue, empty, 
            half_blue, all_blue, empty,
        //    empty, half_white, all_white, empty
        ] {
            ws.write(layout.iter().cloned()).unwrap();
            arduino_hal::delay_ms(1000 as u16);
        }
    }
}
