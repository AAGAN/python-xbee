"""
zigbee.py

By Greg Rapp, 2010
Inspired by code written by Paul Malmsten, 2010
Inspired by code written by Amit Synderman and Marco Sangalli
gdrapp@gmail.com

This module implements an XBee ZB (ZigBee) API library.
"""
import struct
from xbee.base import XBeeBase

class ZigBee(XBeeBase):
    """
    Provides an implementation of the XBee API for XBee ZB (ZigBee) modules
    with recent firmware.
    
    Commands may be sent to a device by instantiating this class with
    a serial port object (see PySerial) and then calling the send
    method with the proper information specified by the API. Data may
    be read from a device (synchronously only, at the moment) by calling 
    wait_read_frame.
    """
    # Packets which can be sent to an XBee
    
    # Format: 
    #        {name of command:
    #           [{name:field name, len:field length, default: default value sent}
    #            ...
    #            ]
    #         ...
    #         }
    api_commands = {"at":
                        [{'name':'id',        'len':1,      'default':'\x08'},
                         {'name':'frame_id',  'len':1,      'default':'\x01'},
                         {'name':'command',   'len':2,      'default':None},
                         {'name':'parameter', 'len':None,   'default':None}],
                    "queued_at":
                        [{'name':'id',        'len':1,      'default':'\x09'},
                         {'name':'frame_id',  'len':1,      'default':'\x01'},
                         {'name':'command',   'len':2,      'default':None},
                         {'name':'parameter', 'len':None,   'default':None}],
                    "remote_at":
                        [{'name':'id',              'len':1,        'default':'\x17'},
                         {'name':'frame_id',        'len':1,        'default':'\x00'},
                         # dest_addr_long is 8 bytes (64 bits), so use an unsigned long long
                         {'name':'dest_addr_long',  'len':8,        'default':struct.pack('>Q', 0)},
                         {'name':'dest_addr',       'len':2,        'default':'\xFF\xFE'},
                         {'name':'options',         'len':1,        'default':'\x02'},
                         {'name':'command',         'len':2,        'default':None},
                         {'name':'parameter',       'len':None,     'default':None}],
                    "tx":
                        [{'name':'id',              'len':1,        'default':'\x10'},
                         {'name':'frame_id',        'len':1,        'default':'\x01'},
                         {'name':'dest_addr_long',  'len':8,        'default':None},
                         {'name':'dest_addr',       'len':2,        'default':None},
                         {'name':'broadcast_radius','len':1,        'default':'\x00'},
                         {'name':'options',         'len':1,        'default':'\x00'},
                         {'name':'data',            'len':None,     'default':None}],
                    "tx_explicit":
                        [{'name':'id',              'len':1,        'default':'\x11'},
                         {'name':'frame_id',        'len':1,        'default':'\x00'},
                         {'name':'dest_addr_long',  'len':8,        'default':None},
                         {'name':'dest_addr',       'len':2,        'default':None},
                         {'name':'src_endpoint',    'len':1,        'default':None},
                         {'name':'dest_endpoint',   'len':1,        'default':None},
                         {'name':'cluster',         'len':1,        'default':None},
                         {'name':'profile',         'len':1,        'default':None},
                         {'name':'broadcast_radius','len':1,        'default':'\x00'},
                         {'name':'options',         'len':1,        'default':'\x00'},
                         {'name':'data',            'len':None,     'default':None}]
                    }
    
    # Packets which can be received from an XBee
    
    # Format: 
    #        {id byte received from XBee:
    #           {name: name of response
    #            structure:
    #                [ {'name': name of field, 'len':length of field}
    #                  ...
    #                  ]
    #            parse_as_io_samples:name of field to parse as io
    #           }
    #           ...
    #        }
    #
    api_responses = {"\x90":
                        {'name':'rx',
                         'structure':
                            [{'name':'source_addr_long','len':8},
                             {'name':'source_addr',     'len':2},
                             {'name':'options',         'len':1},
                             {'name':'rf_data',         'len':None}]},
                     "\x91":
                        {'name':'rx_explicit',
                         'structure':
                            [{'name':'source_addr_long','len':8},
                             {'name':'source_addr',     'len':2},
                             {'name':'source_endpoint', 'len':1},
                             {'name':'dest_endpoint',   'len':1},
                             {'name':'cluster',         'len':2},
                             {'name':'profile',         'len':2},
                             {'name':'options',         'len':1},
                             {'name':'rf_data',         'len':None}]},
                     "\x92": # Checked by GDR-parse_samples_header function appears to need update to support
                        {'name':'rx_io_data_long_addr',
                         'structure':
                            [{'name':'source_addr_long','len':8},
                             {'name':'source_addr',     'len':2},
                             {'name':'options',         'len':1},
                             {'name':'samples',         'len':None}],
                         'parse_as_io_samples':'samples'},
                     "\x8b":
                        {'name':'tx_status',
                         'structure':
                            [{'name':'frame_id',        'len':1},
                             {'name':'dest_addr',       'len':2},
                             {'name':'retries',         'len':1},
                             {'name':'deliver_status',  'len':1},
                             {'name':'discover_status', 'len':1}]},
                     "\x8a":
                        {'name':'status',
                         'structure':
                            [{'name':'status',      'len':1}]},
                     "\x88":
                        {'name':'at_response',
                         'structure':
                            [{'name':'frame_id',    'len':1},
                             {'name':'command',     'len':2},
                             {'name':'status',      'len':1},
                             {'name':'parameter',   'len':None}]},
                     "\x97": #Checked GDR (not sure about parameter, could be 4 bytes)
                        {'name':'remote_at_response',
                         'structure':
                            [{'name':'frame_id',        'len':1},
                             {'name':'source_addr_long','len':8},
                             {'name':'source_addr',     'len':2},
                             {'name':'command',         'len':2},
                             {'name':'status',          'len':1},
                             {'name':'parameter',       'len':None}]},
                     "\x95":
                        {'name':'node_id_indicator',
                         'structure':
                            [{'name':'sender_addr_long','len':8},
                             {'name':'sender_addr',     'len':2},
                             {'name':'options',         'len':1},
                             {'name':'source_addr',     'len':2},
                             {'name':'source_addr_long','len':8},
                             {'name':'node_id',         'len':0},
                             {'name':'parent_source_addr','len':2},
                             {'name':'device_type',     'len':1},
                             {'name':'source_event',    'len':1},
                             {'name':'digi_profile_id', 'len':2},
                             {'name':'manufacturer_id', 'len':2}]}
                     }
    
    def __init__(self, *args, **kwargs):
        # Call the super class constructor to save the serial port
        super(ZigBee, self).__init__(*args, **kwargs)
