"""
    Picasa Web Albums api client module
"""

# main imports
import sys
from urllib import urlencode
import urllib2
import xml.dom.minidom
import datetime


class PicasaClient:
    # base urls
    BASE_URI = "http://picasaweb.google.com/data/feed/api"
    BASE_AUTHENTICATE_URI = "https://www.google.com/accounts/ClientLogin?%s"

    def __getattr__( self, method ):
        def method( _method=method, **params ):
            try:
                # set our base uri
                base_uri = self.BASE_URI
                # add the user_id if it was passed, otherwise assume a search
                if ( params[ "user_id" ] ):
                    base_uri += "/user/" + params[ "user_id" ]
                    if ( _method == "users_contacts" ):
                        base_uri += "/contacts"
                elif ( _method == "featured_photos" ):
                    base_uri += "/featured"
                else:
                    base_uri += "/all"
                # add the album id if it was passed
                if ( params[ "album_id" ] ):
                    base_uri += "/albumid/" + params[ "album_id" ]
                # add our parameter string
                base_uri += "?%s"
                # create the parameter dictionary
                fparams = {}
                for key, value in params.items():
                    if ( value and key != "authkey" and key != "user_id" and key != "contact_id" and key != "album_id" ):
                        fparams[ key.replace( "__", "-" ) ] = value
                # fetch the feed
                xml_data = self._fetch_data( base_uri % ( urlencode( fparams ), ), params[ "authkey" ] )
                # parse the xml data
                if ( _method == "users_contacts" ):
                    items = self._parse_contacts( xml_data )
                else:
                    items = self._parse_data( xml_data, ( params[ "user_id" ] != "" and ( params[ "album_id" ] == "" and not fparams.has_key( "kind" ) ) ) )
            except:
                # oops return an empty list
                items = []
                print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return items
        return method

    def _parse_contacts( self, xml_data ):
        try:
            feed = {}
            items = []
            if ( xml_data ):
                #get our document object
                dom = xml.dom.minidom.parseString( xml_data )
                #print repr( dom.toprettyxml() )
                # parse general info
                totalResults = int( dom.getElementsByTagName( "openSearch:totalResults" )[ 0 ].firstChild.nodeValue )
                # enumerate thru and grab all the required tags
                for node in dom.getElementsByTagName( "entry" ):
                    user = node.getElementsByTagName( "gphoto:user" )[ 0 ].firstChild.nodeValue
                    nickname = node.getElementsByTagName( "gphoto:nickname" )[ 0 ].firstChild.nodeValue
                    thumb_url = node.getElementsByTagName( "gphoto:thumbnail" )[ 0 ].firstChild.nodeValue
                    # add the info to our items list
                    items += [ { "user": user, "nickname": nickname, "thumb_url": thumb_url } ]
                feed = { "totalResults": totalResults, "items": items }
        except:
            # oops return an empty list
            feed = {}
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
        # try to unlink our document object
        try:
            dom.unlink()
        except:
            pass
        # return items
        return feed

    def _parse_data( self, xml_data, isAlbum ):
        try:
            #print xml_data
            feed = {}
            items = []
            if ( xml_data ):
                #get our document object
                dom = xml.dom.minidom.parseString( xml_data )
                #print repr( dom.toprettyxml() )
                # parse general info
                totalResults = int( dom.getElementsByTagName( "openSearch:totalResults" )[ 0 ].firstChild.nodeValue )
                #startindex = int( dom.getElementsByTagName( "openSearch:startIndex" )[ 0 ].firstChild.nodeValue )
                #perpage = int( dom.getElementsByTagName( "openSearch:itemsPerPage" )[ 0 ].firstChild.nodeValue )
                user_id = dom.getElementsByTagName( "gphoto:user" )[ 0 ].firstChild.nodeValue
                try:
                    user_icon = dom.getElementsByTagName( "icon" )[ 0 ].firstChild.nodeValue
                    user_nick = dom.getElementsByTagName( "gphoto:nickname" )[ 0 ].firstChild.nodeValue
                except:
                    user_icon = ""
                    user_nick = ""
                author = ""
                rights = ""
                numphotos = 0
                try:
                    author = dom.getElementsByTagName( "author" )[ 0 ].getElementsByTagName( "name" )[ 0 ].firstChild.nodeValue
                    numphotos = int( dom.getElementsByTagName( "gphoto:numphotos" )[ 0 ].firstChild.nodeValue )
                    rights = dom.getElementsByTagName( "rights" )[ 0 ].firstChild.nodeValue
                except:
                    pass
                # enumerate thru and grab all the required tags
                for node in dom.getElementsByTagName( "entry" ):
                    title = node.getElementsByTagName( "title" )[ 0 ].firstChild.nodeValue
                    summary = ""
                    if ( node.getElementsByTagName( "summary" )[ 0 ].hasChildNodes() ):
                        summary = node.getElementsByTagName( "summary" )[ 0 ].firstChild.nodeValue.encode( "UTF-8", "replace" )
                    if ( author == "" ):
                        author = node.getElementsByTagName( "author" )[ 0 ].getElementsByTagName( "name" )[ 0 ].firstChild.nodeValue
                    # these are only available for album list
                    try:
                        numphotos = int( node.getElementsByTagName( "gphoto:numphotos" )[ 0 ].firstChild.nodeValue )
                        rights = node.getElementsByTagName( "rights" )[ 0 ].firstChild.nodeValue
                    except:
                        pass
                    # currently not used
                    id = node.getElementsByTagName( "id" )[ 0 ].firstChild.nodeValue
                    # should be the only thumb, since we limit size in settings
                    thumb_url = node.getElementsByTagName( "media:group" )[ 0 ].getElementsByTagName( "media:thumbnail" )[ 0 ].getAttribute( "url" )
                    try:
                        # if this is a photo album, id and photo id should be available
                        photo_id = ""
                        photo_url = ""
                        album_id = node.getElementsByTagName( "gphoto:albumid" )[ 0 ].firstChild.nodeValue
                        photo_id = node.getElementsByTagName( "gphoto:id" )[ 0 ].firstChild.nodeValue
                        # we only want to set the photo url for non album lists
                        if ( not isAlbum ):
                            photo_url = node.getElementsByTagName( "media:group" )[ 0 ].getElementsByTagName( "media:content" )[ 0 ].getAttribute( "url" )
                    except:
                        album_id = node.getElementsByTagName( "gphoto:id" )[ 0 ].firstChild.nodeValue
                    # photo size
                    try:
                        photo_size = long( node.getElementsByTagName( "gphoto:size" )[ 0 ].firstChild.nodeValue )
                    except:
                        try:
                            #print node.getElementsByTagName( "media:group" )[ 0 ].getElementsByTagName( "media:content" )[ 0 ].getAttribute( "fileSize" )
                            photo_size = long( node.getElementsByTagName( "media:group" )[ 0 ].getElementsByTagName( "media:content" )[ 0 ].getAttribute( "fileSize" ) )
                        except:
                            photo_size = 0
                    #print "PS", photo_size
                    try:
                        photo_datetime = str( datetime.datetime.fromtimestamp( long( node.getElementsByTagName( "gphoto:timestamp" )[ 0 ].firstChild.nodeValue[ : -3 ] ) ) )
                    except:
                        try:
                            photo_datetime = node.getElementsByTagName( "published" )[ 0 ].firstChild.nodeValue
                        except:
                            photo_datetime = ""
                    try:
                        photo_width = int( node.getElementsByTagName( "gphoto:width" )[ 0 ].firstChild.nodeValue )
                        photo_height = int( node.getElementsByTagName( "gphoto:height" )[ 0 ].firstChild.nodeValue )
                    except:
                        photo_width = -1
                        photo_height = -1
                    # add the info to our items list
                    items += [ { "title": title, "photo_width": photo_width, "photo_height": photo_height, "photo_datetime": photo_datetime, "photo_size": photo_size, "photo_url": photo_url, "album_id": album_id, "user_id": user_id, "photo_id": photo_id, "numphotos": numphotos, "author": author, "summary": summary, "rights": rights, "id": id, "thumb_url": thumb_url } ]
                feed = { "totalResults": totalResults, "user_icon": user_icon, "user_nick": user_nick, "items": items }
        except:
            # oops return an empty list
            feed = {}
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
        # try to unlink our document object
        try:
            dom.unlink()
        except:
            pass
        # return items
        return feed

    def _fetch_data( self, uri, authkey ):
        try:
            # we need to request the uri to be redirected to the proper url
            request = urllib2.Request( uri )
            # if authenticate key exists add it to the header
            if ( authkey ):
                request.add_header( "Authorization", "GoogleLogin auth=%s" % ( authkey, ) )
            # create an opener object to grab the data
            opener = urllib2.build_opener().open( request )
            # read data
            xml_data = opener.read()
            # close opener
            opener.close()
            # return the raw xml data
            return xml_data
        except:
            # oops return an empty string
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return ""

    def authenticate( self, user_id, user_password ):
        import re
        # the needed parameters for authenticating
        auth_request = { "Email": user_id, "Passwd": user_password, "service": "lh2", "accountType": "HOSTED_OR_GOOGLE", "source": "XBMC Picasa" }
        try:
            # we post the needed authentication request to our uri
            request = urllib2.Request( self.BASE_AUTHENTICATE_URI % ( urlencode( auth_request ), ) )
            # add the required header
            request.add_header( "Content-Type", "application/x-www-form-urlencoded" )
            # create an opener object to grab the data
            opener = urllib2.build_opener().open( request )
            # read data
            data = opener.read()
            # close opener
            opener.close()
            # find the authentication key
            authkey = re.findall( "Auth=(.+)", data )[ 0 ]
            # return the authentication key
            return authkey
        except:
            # oops return an empty string
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return ""

if ( __name__ == "__main__" ):
    client = PicasaClient()
    #authkey = client.authenticate( "username", "password" )
    #print "key", authkey
    exec 'feed = client.photos( q="clownfish", user_id="", album_id="", photo_id="", kind="photo", imgmax="d", thumbsize=200, authkey="", access="public", start__index=1, max__results=35 )'
    print feed[ "items" ]
