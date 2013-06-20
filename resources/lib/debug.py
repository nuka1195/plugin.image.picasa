""" debugging module """

import os
import re


class XBMC:
    LOGDEBUG = 0
    LOGNOTICE = 2
    LOGERROR = 4
    CONFIRMED = False
    REGION = { "datelong": "%A,%B %d, %Y", "time": "%I:%M%S %p", "tempunit": "F", "speedunit": "mph" }
    INFOLABEL = { "System.Date": "Friday, July 2, 2010" }

    class Player:
        @staticmethod
        def getTotalTime():
            return 60

        @staticmethod
        def getTime():
            return 10

    class Keyboard:
        def __init__( self, default, heading, hidden=False ):
            pass

        @staticmethod
        def doModal( autoclose=0 ):
            pass

        @staticmethod
        def isConfirmed():
            # only need to test once
            XBMC.CONFIRMED = not XBMC.CONFIRMED
            return XBMC.CONFIRMED

        @staticmethod
        def getText():
            return "AC/DC"

    @staticmethod
    def log( msg, level=0 ):
        print msg

    @staticmethod
    def output( msg, level=0 ):
        print msg

    @staticmethod
    def executebuiltin( function ):
        pass

    @staticmethod
    def sleep( time ):
        pass

    @staticmethod
    def getLanguage():
        return "English"

    @staticmethod
    def getInfoLabel( infotag ):
        return XBMC.INFOLABEL.get( infotag.lower(), "Invalid Id" )

    @staticmethod
    def getCacheThumbName( path ):
        return "".join( [ char for char in path if char.isalnum() ] )

    @staticmethod
    def translatePath( path ):
        return ""

    @staticmethod
    def getRegion( id ):
        return XBMC.REGION.get( id.lower(), "Invalid Id" )


class XBMCGUI:

    class Window:
        @staticmethod
        def __init__( wId=0 ):
            pass

        @staticmethod
        def doModal():
            pass

        class getControl:
            @staticmethod
            def __init__( controlId ):
                pass

            @staticmethod
            def setLabel( label ):
                print label

            @staticmethod
            def reset():
                pass

            @staticmethod
            def setText( text ):
                print text

    class Dialog:
        @staticmethod
        def select( heading, items, autoclose=0 ):
            return 0

        @staticmethod
        def ok( heading, line1="", line2="", line3="" ):
            print "-" * 50
            print heading
            print "-" * 50
            print line1
            print line2
            print line3
            print "-" * 50

    class DialogProgress:
        @staticmethod
        def iscanceled():
            return False

        @staticmethod
        def close():
            pass

        @staticmethod
        def create( heading, line1="", line2="", line3="" ):
            print "-" * 50
            print heading
            print "-" * 50
            print line1
            print line2
            print line3
            print "-" * 50

        @staticmethod
        def update( percent, line1="", line2="", line3="" ):
            print "%d%%" % ( percent, )


class XBMCADDON:
    # dictionary to hold addon info
    INFO = {}
    STRINGS = {}
    SETTINGS = {}

    class Addon:
        def __init__( self, id ):
            # TODO: do we want to use id for anything?
            # get proper path to root folder
            _path = self._get_path( id )
            # parse addon.xml and set all addon info
            self._set_addon_info( _path)
            # parse addon.xml and set all addon strings
            self._set_addon_strings( _path )

        def _get_path( self, id ):
            # path of main addon
            _path = os.getcwd()
            # check if we're at root folder of addon
            if ( not os.path.isfile( os.path.join( _path, "addon.xml" ) ) ):
                # we're not at root, assume resources/lib/
                _path = os.path.dirname( os.path.dirname( os.getcwd() ) )
            # return proper path
            return _path

        def _set_addon_info( self, _path ):
            # get source
            xml = open( os.path.join( _path, "addon.xml" ), "r" ).read()
            # set addon.xml info into dictionary
            XBMCADDON.INFO[ "id" ], XBMCADDON.INFO[ "name" ], XBMCADDON.INFO[ "version" ], XBMCADDON.INFO[ "author" ] = re.search( "<addon id=\"([^\"]+)\".+?name=\"([^\"]+)\".+?version=\"([^\"]+)\".+?provider-name=\"([^\"]+)\".*?>", xml, re.DOTALL ).groups( 1 )
            XBMCADDON.INFO[ "type" ], XBMCADDON.INFO[ "library" ] = re.search(  "<extension point=\"([^\"]+)\".+?library=\"([^\"]+)\".*?>", xml, re.DOTALL ).groups( 1 )
            for metadata in [ "summary", "disclaimer", "description" ]:
                XBMCADDON.INFO[ metadata ] = re.search( "<%s>([^<]*)</%s>" % ( metadata, metadata, ), xml, re.DOTALL ).group( 1 )
            # set other info
            XBMCADDON.INFO[ "path" ] = _path
            XBMCADDON.INFO[ "libpath" ] = os.path.join( _path, XBMCADDON.INFO[ "library" ] )
            XBMCADDON.INFO[ "icon" ] = os.path.join( _path, "icon.png" )
            XBMCADDON.INFO[ "fanart" ] = os.path.join( _path, "fanart.jpg" )
            XBMCADDON.INFO[ "changelog" ] = os.path.join( _path, "changelog.txt" )
            XBMCADDON.INFO[ "profile" ] = "special://profile/addon_data/%s" % ( os.path.basename( _path ), )

        def _set_addon_strings( self, _path ):
            # get source
            xml = open( os.path.join( _path, "resources", "language", "English", "strings.xml" ), "r" ).read()
            # create dictionary
            XBMCADDON.STRINGS = dict( re.findall( "<string id=\"([^\"]+)\">([^<]+)</string>", xml ) )

        @staticmethod
        def getLocalizedString( id ):
            return XBMCADDON.STRINGS.get( str( id ), "Invalid Id" )

        @staticmethod
        def getSetting( id ):
            return XBMCADDON.SETTINGS.get( id, "" )

        @staticmethod
        def setSetting( id, value ):
            XBMCADDON.SETTINGS[ id ] = value

        @staticmethod
        def openSettings():
            pass

        @staticmethod
        def getAddonInfo( id ):
            return XBMCADDON.INFO[ id.lower() ]


if ( __name__ == "__main__" ):
    xbmc = XBMC()
    xbmcgui = XBMCGUI()
    Addon = XBMCADDON().Addon( "python.debug.module" )
    print Addon.getAddonInfo( "Id" )
    print Addon.getAddonInfo( "Type" )
    print Addon.getAddonInfo( "Author" )
    print Addon.getAddonInfo( "Name" )
    print Addon.getAddonInfo( "Version" )
    print Addon.getAddonInfo( "Summary" )
    print Addon.getAddonInfo( "Disclaimer" )
    print Addon.getAddonInfo( "Description" )
    print Addon.getAddonInfo( "Icon" )
    print Addon.getAddonInfo( "Fanart" )
    print Addon.getAddonInfo( "Changelog" )
    print Addon.getAddonInfo( "Path" )
    print Addon.getAddonInfo( "Library" )
    print Addon.getAddonInfo( "Profile" )
    print xbmc.getRegion( "datelong" )
    print Addon.getLocalizedString( 30760 )
