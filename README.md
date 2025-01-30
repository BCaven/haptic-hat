# Haptic Hat: a haptic feedback balance assistant

## the idea

A device that translates incoming data into haptic information - delivering information to the user without sight or sound.
This repository uses data from a gyroscope and compass, but the same idea could be applied to other information, such as sound or artificial input (like system information about a phone or pc).

## hardware

The hat is comprised of a series of vibrational motors that are sewn into the brim of a hat. The motors are controlled by a raspberry pi pico which is attached to the brim of the hat, although the actual location of the controller does not matter.

The complete setup has four parts, the hat (with motors attached), the controller (raspberry pi pico), the battery, and the sensor input.

The hat I made used a MPU9250, although the same idea could be applied to any other data as long as you have a way to get it to the controller.

## software

This project is written in micropython for use on a [raspberry pi pico](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html).

## Research
 - [David Eagleman's TED talk](https://www.ted.com/talks/david_eagleman_can_we_create_new_senses_for_humans)
 - [Livewired: The Inside Story of the Ever-Changing Brain](https://en.wikipedia.org/wiki/Livewired_(book))
