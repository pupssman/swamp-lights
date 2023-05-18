#![no_std]
use arduino_hal::Spi;

use ws2812_spi as ws2812;
use crate::ws2812::Ws2812;
use smart_leds::{SmartLedsWrite};

use blinker_utils::*;  // sister-crate, go with all-imports

pub fn pulse_once(chain: &mut GradientPulserChain, ws: &mut Ws2812<Spi>) {
    for maybe_bulb in &mut chain.gpbs {
        match maybe_bulb {
            None => (),
            Some(ref mut bulb) => {
                let maybe_pulser = &mut bulb.sgps[0];  // FIXME: should use different ones)
                match maybe_pulser {
                    Some(ref mut pulser) => {
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
