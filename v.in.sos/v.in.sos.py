#!/usr/bin/env python
#
############################################################################
#
# MODULE:	    v.in.sos
# AUTHOR(S):	Ondrej Pesek <pesej.ondrek@gmail.com>
# PURPOSE:	    Import data from SOS server as a vector layer to GRASS GIS
# COPYRIGHT:	(C) 2017 Ondrej Pesek and the GRASS Development Team
#
#		This program is free software under the GNU General
#		Public License (>=v2). Read the file COPYING that
#		comes with GRASS for details.
#
#############################################################################

#%module
#% description: Import data from SOS server as a vector layer to GRASS GIS.
#% keyword: vector
#% keyword: import
#% keyword: SOS
#%end
#%flag
#% key: v
#% description: Print observed properties for given url and offering
#% guisection: SOS description
#%end
#%flag
#% key: o
#% description: Print offerings for given url
#% guisection: SOS description
#%end
#%flag
#% key: p
#% description: Print procedures for given url and offering
#% guisection: SOS description
#%end
#%flag
#% key: t
#% description: Print begin and end timestamps for given url and offering
#% guisection: SOS description
#%end
#%option
#% key: url
#% type: string
#% description: Base URL starting with 'http' and ending in '?'
#% required: yes
#%end
#%option G_OPT_V_OUTPUT
#% required: no
#% guisection: Request
#%end
#%option
#% key: offering
#% type: string
#% description: A collection of sensor used to conveniently group them up
#% required: no
#% guisection: Request
#%end
#%option
#% key: response_format
#% type: string
#% options: text/xml;subtype="om/1.0.0", application/json
#% description: Format of data output
#% answer: text/xml;subtype="om/1.0.0"
#% required: no
#% guisection: Request
#%end
#%option
#% key: observed_properties
#% type: string
#% description: The phenomena that are observed
#% required: no
#% guisection: Request
#% multiple: yes
#%end
#%option
#% key: procedure
#% type: string
#% description: Who provide the observations
#% required: no
#% guisection: Request
#%end
#%option
#% key: event_time
#% type: string
#% label: Timestamp of first/timestamp of last requested observation
#% description: Exmaple: 2015-06-01T00:00:00+0200/2015-06-03T00:00:00+0200
#% required: no
#% guisection: Request
#%end
#%option
#% key: version
#% type: string
#% description: Version of SOS server
#% guisection: Request
#% options: 1.0.0, 2.0.0
#% answer: 1.0.0
#%end
#%option
#% key: username
#% type: string
#% description: Username with access to server
#% guisection: User
#%end
#%option
#% key: password
#% type: string
#% description: Password according to username
#% guisection: User
#%end
#%rules
#% requires_all: -v, offering, url
#% requires_all: -p, offering, url
#% requires_all: -t, offering, url
#% requires: -o, url
#%end


import sys
from owslib.sos import SensorObservationService
from grass.script import parser, run_command

sys.path.append('/home/ondrej/workspace/GRASS-GIS-SOS-tools/format_conversions')
# TODO: Incorporate format conversions into OWSLib and don't use absolute path
from xml2geojson import xml2geojson
from json2geojson import json2geojson


def cleanup():
    pass


def main():
    service = SensorObservationService(options['url'],
                                       version=options['version'])

    printing = False

    if flags['o'] is True:
        print('\nSOS offerings:')
        for offering in service.offerings:
            print(offering.name)
        printing = True

    if flags['v'] is True:
        print('\nObserved properties of %s offering:' % options['offering'])
        for observed_property in service[options['offering']].observed_properties:
            print(observed_property)
        printing = True

    if flags['p'] is True:
        print('\nProcedures of %s offering:' % options['offering'])
        for procedure in service[options['offering']].procedures:
            print(procedure)
        printing = True

    if flags['t'] is True:
        print('\nBegin timestamp, end timestamp of %s offering:' % options['offering'])
        print('%s, %s' % (service[options['offering']].begin_position, service[options['offering']].end_position))
        printing = True

    if printing is True:
        sys.exit(0)

    if options['procedure'] == '':
        options['procedure'] = None

    obs = service.get_observation(offerings=[options['offering']],
                                  responseFormat=options['response_format'],
                                  observedProperties=[options['observed_properties']],
                                  procedure=options['procedure'],
                                  username=options['username'],
                                  password=options['password'])

    if options['version'] in ['1.0.0', '1.0'] and str(options['response_format']) == 'text/xml;subtype="om/1.0.0"':
        parsed_obs = xml2geojson(obs)
    elif str(options['response_format']) == 'application/json':
        parsed_obs = json2geojson(obs)

    run_command('v.in.ogr',
                input=parsed_obs,
                output=options['output'],
                flags='o')

    return 0


if __name__ == "__main__":
    options, flags = parser()
    main()
