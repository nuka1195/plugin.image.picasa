## updates module for xbmc4xbox

import sys
import xbmcgui
import xbmcaddon

# Addon class
Addon = xbmcaddon.Addon( id=sys.argv[ 1 ] )


def _check_for_updates():
    try:
        # create dialog
        pDialog = xbmcgui.DialogProgress()
        # give feedback
        pDialog.create( Addon.getAddonInfo( "Name" ), Addon.getLocalizedString( 30760 ) )
        pDialog.update( 0 )
        # url to addon.xml file
        url = "%ssvn/addons/%s/addon.xml" % ( Addon.getSetting( "repo" ), Addon.getAddonInfo( "Id" ), )
        # import here for faster dialog
        import urllib
        import re
        # get addon.xml source
        xml = urllib.urlopen( url ).read()
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
    ok = xbmcgui.Dialog().ok( Addon.getAddonInfo( "Name" ), msg1, "", msg2 )


if ( __name__ == "__main__" ):
    _check_for_updates()
