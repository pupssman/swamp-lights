#![no_std]
#![no_main]

use panic_halt as _;

use arduino_hal::prelude::*;
use arduino_hal::spi;

use ws2812_spi as ws2812;
use crate::ws2812::Ws2812;

use blinker_utils::*;  // sister-crate, go with all-imports
use swamp_blinker::pulse_once;

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

    let mut ws = Ws2812::new(spi);

    // set up serial interface for text output
    let mut serial = arduino_hal::default_serial!(dp, pins, 57600);

    let no_bulb: Option<GradientPulserBulb> = None;
    let mut bulbs = [no_bulb; 10];
    
    bulbs[0] = Some(GradientPulserBulb{
            length: 10,
            current: 0,
            sgps: [
                Some(SingleGradientPulser{
                    start:smart_leds::RGB { r: 100, g: 100, b: 0},
                    end:smart_leds::RGB { r: 0, g: 0, b: 0},
                    period: 30,
                    current: 0
                }), None, None, None
            ]
        });
    
    let mut chain = GradientPulserChain { 
        gpbs: bulbs,
        delay_ms: 100
    };
    ufmt::uwriteln!(&mut serial, "prep done\r").void_unwrap();
    
    loop {
        ufmt::uwriteln!(&mut serial, "loop\r").void_unwrap();
        pulse_once(&mut chain, &mut ws);
        arduino_hal::delay_ms(chain.delay_ms);
    }
}
