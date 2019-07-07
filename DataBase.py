from entities import *

def selectFromById(connection,table_name,id):
    cursor = connection.execute("SELECT * FROM {} WHERE id='{}'".format(table_name,id))
    return cursor

def getAll(connection, table_name):#playlists or artists or bands or albums or songs
    cursor = connection.execute("SELECT * FROM "+table_name)
    objects=[]
    for row in cursor:
        if table_name=="playlist":
            obj = playlist(row[0],row[1],row[2],row[3])#id,name,discription,num of songs
        elif table_name=="artist":
            obj = artist(row[0],row[1],row[2],row[3])#id, name, band id, date of birth
        elif table_name=="band":
            obj = band(row[0],row[1])#id, name
        elif table_name=="album":
            obj = album(row[0],row[1],row[2])#id, title, num of songs
        elif table_name=="song":
            songAlbum=selectFromById(connection,"album",row[6]).fetchmany()
            artists_name=getSongSinger(connection,"song_artist",row[0])
            bands_name  =getSongSinger(connection,"song_band",row[0])
            obj = song(row[0],row[1],row[2],row[3],row[4],row[5],row[6] ,songAlbum[0][1],artists_name, bands_name, row[7])
                      #id    ,name  ,releas,geners,lyrics,length,albumId, album Name    ,artist_name, band_name, path
        objects.append(obj)
    return objects

def getSongs(connection, table_name, obj):#of playlist or band or artist 
    cSongsId =connection.execute("SELECT song_id FROM song_{} WHERE {}_id='{}'".format(table_name,table_name,obj.id))
    songs=[]
    for row in cSongsId:
        songDB=selectFromById(connection,"song",str(row[0])).fetchmany() #songDB => from database
        songAlbum=selectFromById(connection,"album",songDB[0][6]).fetchmany()
        
        artist_name=getSongSinger(connection,"song_artist",row[0])
        band_name  =getSongSinger(connection,"song_band",row[0])
        
        songOP=song(songDB[0][0],songDB[0][1],songDB[0][2],songDB[0][3],songDB[0][4],songDB[0][5],songDB[0][6],songAlbum[0][1],artist_name,band_name,songDB[0][7]) #songOP => song opject 
        #id, name, release date, geners, lyrics, length, album id, album name,artist_name, bandname, path
        songs.append(songOP)
    return songs

def getAlbumSongs(connection, album):
    cSong= connection.execute("SELECT * FROM song WHERE album_id='{}'".format(album.id))
    songs=[]
    for row in cSong:
        artist_name=getSongSinger(connection,"song_artist",row[0])
        band_name  =getSongSinger(connection,"song_band",row[0])
        
        songOP=song(row[0],row[1],row[2],row[3],row[4],row[5],row[6],album.name,artist_name,band_name,row[7])
        songs.append(songOP)
    return songs

def getSongsToGener(connection,gener):# get songs to specific gener
    cSong= connection.execute("SELECT * FROM song WHERE geners='{}'".format(gener))
    songs=[]
    for row in cSong:
        songAlbum=selectFromById(connection,"album",row[6]).fetchmany()
        artist_name=getSongSinger(connection,"song_artist",row[0])
        band_name  =getSongSinger(connection,"song_band",row[0])
        
        songOP=song(row[0],row[1],row[2],row[3],row[4],row[5],row[6],songAlbum[0][1],artist_name,band_name,row[7])
        songs.append(songOP)
    return songs

def getSongSinger(connection, table_name, song_id): #Singer could be band or artist
    singer= connection.execute("SELECT * FROM {} WHERE song_id='{}'".format(table_name,song_id))
    singers=[]
    for row in singer:
        if table_name=="song_artist":
            artistDB=selectFromById(connection,"artist",row[1]).fetchmany()
            #print(artistDB)
            artistOP=artist(artistDB[0][0],artistDB[0][1],artistDB[0][2],artistDB[0][3])
            singers.append(artistOP.name)
        elif table_name=="song_band":
            bandDB=selectFromById(connection, "band",row[1]).fetchmany()
            bandOP=band(bandDB[0][0],bandDB[0][1])
            singers.append(bandOP.name)
    return singers

def getArtistBand(connection,band):#artist of the band 
    artist= connection.execute("SELECT * FROM artist WHERE band_id='{}'".format(band.id)).fetchmany()
    artists=[]
    for row in artist:
        artistt = artist(row[0],row[1],row[2],row[3])#id, name, band id, date of birth
        artists.append(artistt)
    return artists

def getBandArtist(connection, artist):#band of artist
    bandDB = connection.execute("SELECT * FROM band WHERE id='{}'".format(artist.band_id)).fetchmany()
    bandOP = band(bandDB[0][0],bandDB[0][1])
    return bandOP

def getGeners(connection):
	cursor = connection.execute("SELECT DISTINCT geners FROM song")
	geners = []
	gener  = cursor.fetchone()
	while gener is not None:
		geners.append(gener[0])
		gener  = cursor.fetchone()
	return geners
	
	
def ByName(songs,reverse): #sort songs by name, reverse could be true or false
    if reverse:
        songs.sort(key=lambda x: x.name, reverse=True)
    else:
        songs.sort(key=lambda x: x.name, reverse=False)
    return songs

def ByArtist(songs):#sort songs by artist
    songs.sort(key=lambda x: x.artist_name, reverse=False)
    return songs

def ByAlbum(songs):#sort songs by album
    songs.sort(key=lambda x: x.album_id, reverse=False)
    return songs

def ByGeners(songs):#sort songs by geners
    songs.sort(key=lambda x: x.geners, reverse=False)
    return songs

def ByReleaseDate(songs):#sort songs by release date
    songs.sort(key=lambda x: str(x.releaseDate), reverse=False)
    return songs

def addPlayList(connection,playlist):
    connection.execute("INSERT INTO playlist (name, description,numOfSongs) values('{}','{}','{}');".format(playlist.name,playlist.description,playlist.numOfSongs))
    connection.commit()

def addSongToPlayList(connection,song,playlist):
    connection.execute("INSERT INTO song_playlist (song_id, playlist_id) values({},{});".format(song.id,playlist.id))
    connection.execute("UPDATE playlist SET numOfSongs='{}' WHERE id='{}';".format(str(playlist.numOfSongs+1) , str(playlist.id)))#update num of songs in playlist table
    connection.commit()

def addArtist(connection,artist):
    x = connection.execute("INSERT INTO artist (name,dateOfBirth) values('{}','{}');".format(artist.name,artist.dateOfBirth))
    connection.commit()
    return x

def addSong(connection,song,artist_id):
    x= connection.execute("INSERT INTO song (name, releaseDate, geners, lyrics, length, album_id, path) values('{}','{}','{}','{}','{}','{}','{}');".format(song.name,song.releaseDate,song.geners,song.lyrics,song.length,song.album_id,song.path))
    connection.execute("INSERT INTO song_artist (song_id, artist_id) values('{}','{}')".format(x.lastrowid,artist_id))
    connection.commit()

def addAlbum(connection,album):
    connection.execute("INSERT INTO album (title, numOfSongs) values('{}','{}');".format(album.name,album.numOfSongs))
    connection.commit()

def removeSongFromPlaylist(connection,song,playlist):
    connection.execute("DELETE FROM song_playlist WHERE song_id='{}' AND playlist_id='{}'".format(song.id,playlist.id))
    connection.execute("UPDATE playlist SET numOfSongs=numOfSongs-1 where id={}".format(playlist.id))
    connection.commit()

def deletePlaylist(connection,playlist):
    connection.execute("DELETE FROM playlist WHERE id={};".format(playlist.id))
    connection.execute("DELETE FROM song_playlist WHERE playlist_id={};".format(playlist.id))
    connection.commit()

def deleteArtist(connection,artist):
    connection.execute("DELETE FROM artist WHERE id={};".format(artist.id))
    connection.execute("DELETE FROM song_artist WHERE artist_id={};".format(artist.id))
    connection.commit()

def deleteSong(connection,song):
    albumId = song.album_id
    playlists = connection.execute("SELECT playlist_id FROM song_playlist WHERE song_id={};".format(song.id)).fetchmany()
    
    
    connection.execute("UPDATE album SET numOfSongs=numOfSongs-1 where id={}".format(albumId))
    connection.commit()
    
    if len(playlists)>0:
        for pid in playlists:
            connection.execute("UPDATE playlist SET numOfSongs=numOfSongs-1 where id={}".format(pid[0]))
        connection.commit()
    connection.execute("DELETE FROM song_playlist WHERE song_id={};".format(song.id))
    connection.execute("DELETE FROM song_artist WHERE song_id={};".format(song.id))
    connection.execute("DELETE FROM song_band WHERE song_id={};".format(song.id))
    
    connection.execute("DELETE FROM song WHERE id={};".format(song.id))
    connection.commit()

def deleteAlbum(connection,album):
    songs_id=connection.execute("SELECT id FROM song WHERE album_id={};".format(album.id))
    for row in songs_id:
        songaa = song(row[0],"","","","","",album.id,"","","","")
        deleteSong(connection,songaa)
    connection.execute("DELETE FROM album WHERE id={};".format(album.id))
    
    connection.commit()
 