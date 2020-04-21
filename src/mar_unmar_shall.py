#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 04:01:56 2020

@author: csy
"""

HEX_DIC = {10: "A", 11: "B", 12: "C", 13: "D", 14: "E", 15: "F"}
"""
This function encodes the messages
which allows the server and the clients
to communicate.
"""
def __marshall__(s):
    if type(s) == int:
        s = str(s)
    hex_list = []
    for c in s:
        num = ord(c)
        dec = str(int(num / 16))
        rem = str(__int_to_hex__(num))
        d = "".join([dec, rem])
        h = bytearray.fromhex(d)
        hex_list.append(h)
    return b"".join(hex_list)


"""
This function decodes the messages
shared by the server and the clients.
"""
def __unmarshall__(b, d_t=str):
    if b == None:
        return b
    hex_list = b.hex()
    char_list = []
    for i in range(int(len(hex_list) / 2)):
        h = hex_list[i * 2 : i * 2 + 2]
        o = int(h[0]) * 16
        t = __hex_to_int__(h[1])
        num = o + t
        char_list.append(chr(num))
    if d_t == int:
        return int("".join(char_list))
    elif d_t == bool:
        return bool("".join(char_list))
    return "".join(char_list)


"""
This function converts integer to hexadecimal.
"""
def __int_to_hex__(a):
    r = a % 16
    if r in list(HEX_DIC.keys()):
        r = HEX_DIC[r]
    return r


"""
This function converts hexadecimal to integer.
"""
def __hex_to_int__(h):
    try:
        h = int(h)
    except ValueError:
        k_list = list(HEX_DIC.keys())
        v_list = list(HEX_DIC.values())
        h = int(k_list[v_list.index(h.upper())])
    return h
