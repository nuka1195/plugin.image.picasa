""" xbox compatibilty module """

__all__ = [ "XBMCADDON" ]

import os
import xbmc
import re

# get current working directory
cwd = os.getcwd()
# check if we're at root folder of addon
if ( not os.path.isfile( os.path.join( cwd, "addon.xml" ) ) ):
    # we're not at root, assume resources/lib/
    cwd = os.path.dirname( os.path.dirname( os.getcwd() ) )

# language module
_language_ = xbmc.Language( cwd ).getLocalizedString
# settings module, try catch necessary as not all scripts have settings
try:
    _settings_ = xbmc.Settings( cwd )
except:
    _settings_ = None


class XBMCADDON:
    """
        xbmcaddon module class
    """
    # dictionary to hold addon info
    INFO = {}

    class Addon:
        """
            Class to emulate xbmcaddon.Addon methods.
        """
        def __init__( self, id ):
            # TODO: do we want to use id for anything?
            # parse addon.xml and set all addon info
            self._set_addon_info( id )

        def _set_addon_info( self, id ):
            # get source
            xml = open( os.path.join( cwd, "addon.xml" ), "r" ).read()
            # set addon.xml info into dictionary
            XBMCADDON.INFO[ "id" ], XBMCADDON.INFO[ "name" ], XBMCADDON.INFO[ "version" ], XBMCADDON.INFO[ "author" ] = re.search( "<addon id=\"([^\"]+)\".+?name=\"([^\"]+)\".+?version=\"([^\"]+)\".+?provider-name=\"([^\"]+)\".*?>", xml, re.DOTALL ).groups( 1 )
            XBMCADDON.INFO[ "type" ], XBMCADDON.INFO[ "library" ] = re.search(  "<extension point=\"([^\"]+)\".+?library=\"([^\"]+)\".*?>", xml, re.DOTALL ).groups( 1 )
            # reset this to default.py as that's what xbox uses
            XBMCADDON.INFO[ "library" ] = "default.py"
            for metadata in [ "summary", "disclaimer", "description" ]:
                XBMCADDON.INFO[ metadata ] = re.search( "(?:<%s>([^<]*)</%s>)?" % ( metadata, metadata, ), xml, re.DOTALL ).group( 1 )
            # set other info
            XBMCADDON.INFO[ "path" ] = cwd
            XBMCADDON.INFO[ "libpath" ] = os.path.join( cwd, XBMCADDON.INFO[ "library" ] )
            XBMCADDON.INFO[ "icon" ] = os.path.join( cwd, "default.tbn" )
            XBMCADDON.INFO[ "fanart" ] = os.path.join( cwd, "fanart.jpg" )
            XBMCADDON.INFO[ "changelog" ] = os.path.join( cwd, "changelog.txt" )
            if ( cwd.startswith( "Q:\\plugins" ) and not cwd.startswith( "Q:\\plugins\\weather" ) ):
                XBMCADDON.INFO[ "profile" ] = "special://profile/plugin_data/%s/%s" % ( os.path.basename( os.path.dirname( cwd ) ), os.path.basename( cwd ), )
            else:
                XBMCADDON.INFO[ "profile" ] = "special://profile/script_data/%s" % ( os.path.basename( cwd ), )

        @staticmethod
        def getLocalizedString( id ):
            return _language_( id )

        @staticmethod
        def getSetting( id ):
            return _settings_.getSetting( id )

        @staticmethod
        def setSetting( id, value ):
            _settings_.setSetting( id, value )

        @staticmethod
        def openSettings():
            _settings_.openSettings()

        @staticmethod
        def getAddonInfo( id ):
            return XBMCADDON.INFO[ id.lower() ]


def _check_for_updates():
    try:
        # import needed classes
        from xbmcgui import Dialog, DialogProgress
        # create dialog
        pDialog = DialogProgress()
        # Addon class
        Addon = XBMCADDON().Addon( id=os.path.basename( cwd ) )
        # give feedback
        pDialog.create( Addon.getAddonInfo( "Name" ), Addon.getLocalizedString( 30760 ) )
        pDialog.update( 0 )
        # import module
        import urllib2
        # url to addon.xml file
        url = "%ssvn/addons/%s/addon.xml" % ( Addon.getSetting( "Repo" ), Addon.getAddonInfo( "Id" ), )
        # get addon.xml source
        xml = urllib2.urlopen( url ).read()
        # parse version
        version = re.search( "<addon id=\"[^\"]+\".+?name=\"[^\"]+\".+?version=\"([^\"]+)\".+?provider-name=\"[^\"]+\".*?>", xml, re.DOTALL ).group( 1 )
        # set proper message
        msg1 = Addon.getLocalizedString( 30700 ) % ( Addon.getAddonInfo( "Version" ), )
        msg2 = [ Addon.getLocalizedString( 30701 ), Addon.getLocalizedString( 30702 ) % ( version, ) ][ version > Addon.getAddonInfo( "Version" ) ]
    except Exception, e:
        # set proper error messages
        msg1 = Addon.getLocalizedString( 30770 )
        msg2 = str( e )
    # done, close dialog
    pDialog.close()
    # notify user of result
    ok = Dialog().ok( Addon.getAddonInfo( "Name" ), msg1, "", msg2 )


if ( __name__ == "__main__" ):
    # xbox doesn't support pysvn
    _check_for_updates()
