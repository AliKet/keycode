/* This file is automatically generated. */
#include "keytable.h"
static const char KEYCODE_WINDOWS_RAWNAME_DATA[] =
    "\0A\0B\0Backslash\0C\0Caps Lock\0Comma\0D\0Delete\0Delete Forward\0E\0End"
    "\0Equals\0Escape\0F\0F1\0F10\0F11\0F12\0F2\0F3\0F4\0F5\0F6\0F7\0F8\0F9\0G"
    "\0Grave\0H\0Home\0Insert\0J\0K\0L\0Left\0Left Alt\0Left Bracket\0Left Con"
    "trol\0Left GUI\0Left Shift\0M\0Minus\0N\0O\0P\0Page Down\0Page Up\0Pause"
    "\0Period\0Print Screen\0Q\0Quote\0R\0Return\0Right\0Right Alt\0Right Brac"
    "ket\0Right Control\0Right GUI\0Right Shift\0S\0Scroll Lock\0Semicolon\0Sl"
    "ash\0T\0Tab\0U\0V\0W\0X\0Y\0Z";
static const unsigned short KEYCODE_WINDOWS_RAWNAME_OFFSET[] = {
    0,70,80,92,98,101,104,107,110,113,116,84,208,63,35,379,264,387,57,272,377,
    391,383,193,216,218,160,297,274,173,1,347,33,77,118,126,140,142,144,361,266,
    120,195,5,393,389,15,385,3,214,206,27,244,371,335,0,151,0,17,79,94,97,100,
    103,106,109,112,115,82,238,349,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,86,90,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,311,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,251,287,0,0,0,0,0,0,0,0,0,0,0,0,0,0,128,235,
    230,0,146,0,281,0,59,225,220,133,42,0,0,0,0,0,0,0,186,325
};
const char *keycode_windows_rawname(unsigned index) {
    unsigned offset;
    if (221 <= index)
        return 0;
    offset = KEYCODE_WINDOWS_RAWNAME_OFFSET[index];
    if (offset == 0)
        return 0;
    return KEYCODE_WINDOWS_RAWNAME_DATA + offset;
}
