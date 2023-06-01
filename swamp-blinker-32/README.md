# Esp32-based blinker

Based on `Rust on ESP32 STD demo app`

A demo STD binary crate for the ESP32[XX] and ESP-IDF, which connects to WiFi, Ethernet, drives a small HTTP server and draws on a LED screen.


## Build

- Install the [Rust Espressif compiler toolchain and the Espressif LLVM Clang toolchain](https://github.com/esp-rs/rust-build)
  - This is necessary, because support for the Xtensa architecture (ESP32 / ESP32-S2 / ESP32-S3) is not upstreamed in LLVM yet
- Switch to the `esp` toolchain from the pre-built binaries: `rustup default esp`
- If using the custom Espressif Clang, make sure that you DON'T have a system Clang installed as well, because even if you have the Espressif one first on your `$PATH`, Bindgen will still pick the system one
- `cargo install ldproxy`
- Export two environment variables that would contain the SSID & password of your wireless network:
  - `export RUST_ESP32_STD_DEMO_WIFI_SSID=<ssid>`
  - `export RUST_ESP32_STD_DEMO_WIFI_PASS=<password>`
- To configure the demo for your particular board, please uncomment the relevant [Rust target for your board](https://github.com/ivmarkov/rust-esp32-std-demo/blob/main/.cargo/config.toml#L2) and comment the others. Alternatively, just append the `--target <target>` flag to all `cargo build` lines below.
- Build: `cargo build` or `cargo build --release`

## QEMU

- Rather than flashing on the chip, you can now run the demo in QEMU:
  - Clone and then build [the Espressif fork of QEMU](https://github.com/espressif/qemu) by following the [build instructions](https://github.com/espressif/qemu/wiki)
  - Uncomment `CONFIG_ETH_USE_OPENETH=y`, `CONFIG_MBEDTLS_HARDWARE_AES=n`, and `CONFIG_MBEDTLS_HARDWARE_SHA=n` in `sdkconfig.defaults.esp32` (it is not enabled by default because this somehow causes issues when compiling for the ESP32S2)
  - Build the app with `cargo build --features qemu`
  - NOTE: Only ESP32 is supported for the moment, so make sure that the `xtensa-esp32-espidf` target (the default one) is active in your `.cargo/config.toml` file (or override with `cargo build --features qemu --target xtensa-esp32-espidf`)
  - Run it in QEMU by typing `./qemu.sh`. NOTE: You might have to change the `ESP_QEMU_PATH` in that script to point to the `build` subdirectory of your QEMU Espressif clone

## Flash

- `cargo install espflash`
- `espflash /dev/ttyUSB0 target/[xtensa-esp32-espidf|xtensa-esp32s2-espidf|riscv32imc-esp-espidf]/debug/rust-esp32-std-demo`
- Replace `dev/ttyUSB0` above with the USB port where you've connected the board

**NOTE**: The above commands do use [`espflash`](https://crates.io/crates/espflash) and NOT [`cargo espflash`](https://crates.io/crates/cargo-espflash), even though both can be installed via Cargo. `cargo espflash` is essentially `espflash` but it has some extra superpowers, like the capability to build the project before flashing, or to generate an ESP32 .BIN file from the built .ELF image.

## Alternative flashing

- You can also flash with the [esptool.py](https://github.com/espressif/esptool) utility which is part of the Espressif toolset
- Use the instructions below **only** if you have flashed successfully with `espflash` at least once, or else you might not have a valid bootloader and partition table!
- The instructions below only (re)flash the application image, as the (one and only) factory image starting from 0x10000 in the partition table!
- Install esptool using Python: `pip install esptool`
- (After each cargo build) Convert the elf image to binary: `esptool.py --chip [esp32|esp32s2|esp32c3] elf2image target/xtensa-esp32-espidf/debug/rust-esp32-std-demo`
- (After each cargo build) Flash the resulting binary: `esptool.py --chip [esp32|esp32s2|esp32c3] -p /dev/ttyUSB0 -b 460800 --before=default_reset --after=hard_reset write_flash --flash_mode dio --flash_freq 40m --flash_size 4MB 0x10000 target/xtensa-esp32-espidf/debug/rust-esp32-std-demo.bin`

## Monitor

- Once flashed, the board can be connected with any suitable serial monitor, e.g.:
  - (Recommended) `espflash`: `espflash serial-monitor`
