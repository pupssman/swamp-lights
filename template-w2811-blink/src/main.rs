#![no_std]
#![no_main]

use panic_halt as _;

use arduino_hal::prelude::*;
use arduino_hal::spi;

use ws2812_spi as ws2812;
use crate::ws2812::prerendered::Ws2812;
use smart_leds::{SmartLedsWrite, RGB8};

use template_w2811_blink::{TOTAL_LEDS, SingleColorLine as SCL};


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

    let pulse_one = [
        SCL{r: 0x00, g: 0x00, b: 0x00},
        SCL{r: 0x00, g: 0x01, b: 0x00},
        SCL{r: 0x00, g: 0x02, b: 0x00},
        SCL{r: 0x00, g: 0x03, b: 0x00},
        SCL{r: 0x00, g: 0x04, b: 0x01},
        SCL{r: 0x00, g: 0x08, b: 0x01},
        SCL{r: 0x00, g: 0x16, b: 0x02},
        SCL{r: 0x00, g: 0x20, b: 0x02},
        SCL{r: 0x00, g: 0x16, b: 0x01},
        SCL{r: 0x00, g: 0x08, b: 0x01},
        SCL{r: 0x00, g: 0x04, b: 0x00},
        SCL{r: 0x00, g: 0x03, b: 0x00},
        SCL{r: 0x00, g: 0x02, b: 0x00},
        SCL{r: 0x00, g: 0x01, b: 0x00},
        SCL{r: 0x00, g: 0x00, b: 0x00},
    ];

    let mut ws = Ws2812::new(spi, &mut output_buffer);

    // set up serial interface for text output
    let mut serial = arduino_hal::default_serial!(dp, pins, 57600);

    loop {
        ufmt::uwriteln!(&mut serial, "loop\r").void_unwrap();

        for layout in pulse_one {
            ws.write(layout.into_iter()).unwrap();
            arduino_hal::delay_ms(100 as u16);
        }
    }
}
