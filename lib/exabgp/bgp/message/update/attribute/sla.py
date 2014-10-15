# encoding: utf-8
"""
sla.py

3.  QoS Attribute Definition

   The QoS Attribute proposed here is an optional transitive attribute
   (attribute type code to be assigned by IANA).  SLA is defined as one
   of the sub-types in the QoS attribute.


       0                   1                   2                   3
       0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |   Attr flag   | Attr type QoS |                               |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               |
       ~                                                               ~
       |                     QoS Attr length/Value                     |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+..........................

    Attribute flags
        highest order bit (bit 0) -
            MUST be set to 1, since this is an optional attribute

        2nd higher order bit (bit 1) -
            MUST be set to 1, since this is a transitive attribute

3.1.  SLA, QoS attribute sub-type, Definition

   The value field of the QoS Attribute contains TLVs, followed to QoS
   Attribute flags described in the previous section.  One of the TLVs
   that we define is a tuple of (SLA sub-type, Length, Value)

       0                   1                   2                   3
       0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       | QoS Attr flags|      subType  |         sub type Length       |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       ~                                                               ~
       |                               Value                           |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+..........................

    The first octet in the Value field of the QoS attribute is QoS
    attribute specific flags

        highest order bit (bit 0) -
            It defines if update message MUST be dropped (if set to 1)
            without updating routing information base, when this is the
            last BGP receiver from the list of destination ASes this
            attribute is announced to, or MUST announce (if set to 0)
            further to BGP peers

            The purpose of this bit is discussed further in subsequent
            sections.

        Remaining bits are currently unused and MUST be set to 0


    subType - 8 bits
        0x00        = reserved
        0x01        = SLA
        0x02 - 0x0f = for future use

    SLA sub-type specific value field details. These details contain
    information about 1) sender and receiver(s) and 2) SLA parameters.
    SLA Parameters include SLA event type (such as Advertise, Request)
    and contents associated to that event type.

    The format of SLA message is,
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                    32-bit source AS (Advertiser)              |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |Optional advertiserid total len|      Advertiser id TLVs       |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+                               ~
       |                                                               |
       ~                                                               ~
       |                                                               |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                  32-bit destination AS count                  |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                variable list of destination AS                |
       ~                            ....                               ~
       |                            ....                               |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       | Event |             SLA id            |      SLA length       |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                    Content as per SLA Event                   |
       ~                                                               ~
       |                                                               |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    Source AS
        32-bit source AS number. This is the AS that is advertising SLA
        0 = ignore Source and Destination AS list from this Value field.
            Instead refer to Source and Destination AS as defined by BGP
            message.

    Optional advertiser id total len
        16-bit Source address identifier (optional).
        0 = No optional identifier

        In general any additional qualifier for an advertiser is not
        required. The SLA definition is in the context of prefix
        advertised in the NLRI definition. The exception is where a BGP
        speaker, in the middle of an update path to the destination AS,
        aggregates prefixes. We will refer this middle BGP speaker, that
        aggregates routes, as an Aggregator. Aggregator is then required
        to insert original NLRI details in the optional advertiser field

    Optional Advertiser id TLV
        4-bit type
        0x0  = reserved
        0x1  = ORIGIN_NLRI, variable length
        0x2 to 0xf = for future use,

    Destination AS count
        32-bit destination AS count to take variable length AS list.
        This count has no functional value when Source AS is 0

        0 = QoS attribute is relevant to every receiver of the message

    Destination AS list
        32-bit destination AS number
        ....
        .... [as many as AS count]

    SLA Event Type
        4-bits
        0x0 = reserved
        0x1 = ADVERTISE
        0x2 = REQUEST
        0x3 to 0xf, for future use

    SLA Id
        16-bit identifier unique within the scope of source AS

        The significance of an SLA identifier is in the context of the
        source that is advertising SLA parameters. The SLA identifier
        is not globally unique but it MUST be unique within the source
        AS (advertiser).

        The SLA content is optional for an advertised SLA id. If SLA
        content does not exist in BGP update messages with advertised
        QoS attribute, that contains the SLA sub-type, then receiver
        MUST inherit prior advertised SLA content for the same SLA id
        from the same Source AS.

        If advertised SLA id is different from earlier advertised one,
        for the same prefix, previous SLA content MUST be replaced
        with the new advertised one.

        SLA is aggregate for all the traffic to prefixes that share
        same source AS and SLA id.

    SLA Length
        12-bits

    The format of SLA ADVERTISE event message is,

       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |dir|       Traffic Class count     | Class Desc Len|           |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+           ~
       |                                                               |
       ~                  Traffic Class Description                    ~
       |                                                               |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                                                               |
       ~              Traffic Class Elements count/values              ~
       |                                                               |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       | Service  Count|      service type/value pair                  |
       +-+-+-+-+-+-+-+-+                                               ~
       |                                                               |
       ~                                                               ~
       |                                                               |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                                                               |
       ~  Repeat from Traffic Class Description for next Traffic Class ~
       |                                                               |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
       |                                                               |
       ~    Repeat from direction for SLA in the other direction       ~
       |                                                               |
       +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

"""

from struct import pack
from struct import unpack

from exabgp.protocol.ip import IPv4
from exabgp.bgp.message.update.attribute.attribute import Attribute

# ========================================================================= PMSI
# draft sla

class SLA (Attribute):
        ID = Attribute.ID.SLA
        FLAG = Attribute.Flag.OPTIONAL
        MULTIPLE = False
        CACHING = True

        __slots__ = ['label','flags','tunnel'] (What to be updated to?)

        def __init__ (self,tunnel,label,flags):
                self.label = label    # integer
                self.flags = flags    # integer


        def pack(self):  (To be updated to SLA TLVs, how?)
                return self._attribute(
                        pack('!BB3s',
                                self.flags,
                                self.TUNNEL_TYPE,
                                pack('!L',self.label << 4)[1:4]
                        )
                )

        def unpack (cls,data,negotiated): (To be updated to SLA TLVs, how?)
                flags,subtype = unpack('!BB',data[:2])
                label = unpack('!L','\0'+data[2:5])[0] >> 4
                # should we check for bottom of stack before the shift ?
                if subtype in cls._pmsi_known:
                        return cls._pmsi_known[subtype].unpack(data[5:],label,flags)
                return cls.pmsi_unknown(subtype,data[5:],label,flags)
