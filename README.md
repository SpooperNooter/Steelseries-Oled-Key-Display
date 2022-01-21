# Steelseries-Oled-Key-Display
(wip) Simple (very rough) program to display pressed keystrokes on one of steelseries apex keyboards

# How to run
Download the code, then run Oled_app.py

# How it works
There's three main programs, BuiltInModules, Oled_app, and UtilityModules. 

Oled_app mainly ties the two other programs together, run this program to run everything else.

UltilityModules is a set of python classes, with functionality like creating and altering bitmaps.

Just a note for the sprite utility module, it takes the name of a directory, within which should be two files, a spritesheet (named sheet.png), and a json file (named info.json), I generated both using aseprite, so they both use aseprites format. It looks in the Animations directory for the sprite.

BuiltInModules is just a few programs that I created using the above two

The animations directory is what is says on the box, a directory for animations
