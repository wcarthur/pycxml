import math
import numpy as np
import numpy.ma as ma


def convert(value, inunits, outunits):
    """
    Convert value from input units to output units.

    :param value: Value to be converted
    :param str inunits: Input units.
    :param str outunits: Output units.

    :returns: Value converted to ``outunits`` units.

    """
    startValue = value
    value = ma.array(value, dtype=float)
    if inunits == outunits:
        # Do nothing:
        return value
    if inunits == 'kmh':
        inunits = 'kph'
    if inunits == 'km/h':
        inunits = 'kph'
    if inunits == "m/s":
        inunits = "mps"
    if inunits == "m s-1":
        inunits = "mps"
    if inunits == 'kt':
        inunits = 'kts'
    if inunits == 'kn':
        inunits = 'kts'

    # Speeds:
    mps = {"kph": 3.6, "kts": 1.944, "mph": 2.2369}
    mph = {"kph": 1.60934, "kts": 0.86898, "mps": 0.44704}
    kph = {"kts": 0.539957, "mps": 0.2777778, "mph": 0.621371}
    kts = {"kph": 1.852, "mps": 0.5144, "mph": 1.15}

    # Temperatures:
    C = {"F": 1.8,
         "K": 1.}
    F = {"C": 0.5556}
    K = {"C": 1.}

    # Pressures:
    kPa = {"hPa": 10., "Pa": 1000.,
           "inHg": 0.295299831,
           "mmHg": 7.500615613,
           "Pascals": 1000.}
    hPa = {"kPa": 0.1, "Pa": 100.,
           "inHg": 0.02953,
           "mmHg": 0.750061561,
           "Pascals": 100.}
    Pa = {"kPa": 0.001,
          "hPa": 0.01,
          "inHg": 0.0002953,
          "mmHg": 0.007500616,
          "Pascals": 1.0}
    inHg = {"kPa": 3.386388667,
            "hPa": 33.863886667,
            "Pa": 3386.388666667,
            "mmHg": 25.4}
    mmHg = {"kPa": 0.13332239,
            "hPa": 1.3332239,
            "Pa": 133.32239,
            "inHg": 0.0394}
    pascals = {"kPa": 0.001,
               "hPa": 0.01,
               "inHg": 0.0002953,
               "mmHg": 0.007500616,
               "Pa": 1.0}

    # Lengths:
    km = {"m": 1000.,
          "mi": 0.621371192,
          "deg": 0.00899886,
          "nm": 0.539957,
          "rad": 0.0001570783}
    deg = {"km": 111.1251,
           "m": 111125.1,
           "mi": 69.0499358,
           "nm": 60.0,
           "rad": math.pi/180.}
    m = {"km": 0.001,
         "mi": 0.000621371,
         "deg": 0.00000899886,
         "nm": 0.000539957,
         "rad": 0.0000001570783}
    mi = {"km": 1.60934,
          "m": 1609.34,
          "deg": 0.014482}
    nm = {"km": 1.852,
          "m": 1852,
          "deg": 0.01666,
          "rad": math.pi/10800.}
    rad = {"nm": 10800./math.pi,
           "km": 6366.248653,
           "deg": 180./math.pi}

    # Mixing ratio:
    gkg = {"kgkg": 0.001}
    kgkg = {"gkg": 1000}

    convert = {"mps": mps,
               "mph": mph,
               "kph": kph,
               "kts": kts,
               "kPa": kPa,
               "hPa": hPa,
               "Pa": Pa,
               "Pascals": pascals,
               "inHg": inHg,
               "mmHg": mmHg,
               "C": C,
               "F": F,
               "K": K,
               "km": km,
               "m": m,
               "deg": deg,
               "mi": mi,
               "nm": nm,
               "rad": rad,
               "gkg": gkg,
               "kgkg": kgkg}

    # Additions required before multiplication:
    convert_pre = {"F": {"C": -32.}}
    # Additions required after multiplication:
    convert_post = {"C": {"K": 273.,
                          "F": 32.},
                    "K": {"C": -273.}}

    if inunits in convert_pre:
        if outunits in convert_pre[inunits]:
            value += convert_pre[inunits][outunits]

    if inunits in convert:
        if outunits in convert[inunits]:
            value = value * convert[inunits][outunits]

    if inunits in convert_post:
        if outunits in convert_post[inunits]:
            value += convert_post[inunits][outunits]

    return value
