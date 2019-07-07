import kivy
kivy.require("1.9.0")
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.listview import ListItemButton
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.weakproxy import WeakProxy
import DataBase as db
from entities import *
import entities as en
import sqlite3
import time
import tkinter 
from tkinter import messagebox
from tkinter import filedialog
from os import walk  
import os
from tinytag import TinyTag

class ProjectListButton(ListItemButton):
    pass

class HomeScreen(Screen):
    
    def most_common(self,lst):
        return max(set(lst), key=lst.count)
    def addAlbum(self):
        con = sqlite3.connect('musicly.db')

        main_win = tkinter.Tk()
        main_win.geometry("300x300")
        main_win.sourceFolder = ''
        main_win.sourceFolder =  filedialog.askdirectory(parent=main_win, initialdir= "/", title='Please select a directory')
        b_chooseDir = tkinter.Button(main_win, text = "Chose Folder", width = 20, height = 3)
        b_chooseDir.place(x = 50,y = 50)
        b_chooseDir.width = 100

        main_win.mainloop()
        if main_win.sourceFolder == "":
            return
        path = main_win.sourceFolder
        f = []
        songss= []
        for (dirpath, dirnames, filenames) in walk(main_win.sourceFolder):
            f.extend(filenames)
            break
        albums_name=[]
        artist_name=""
        artist_id =-1
        for i in range(len(f)):
            if f[i][-3:] == "mp3" or f[i][-3:] == "MP3":
                tag = TinyTag.get(path + '\\' +  f[i])
                if tag.album == None:
                    albums_name.append(path.rsplit('/', 1)[1])
                else:    
                   albums_name.append(tag.album)        
                if tag.title == None or tag.title == "" or tag.title == "None":
                    tag.title = f[i]    
                song= en.song(0,tag.title,tag.year,tag.genre,"",tag.duration,0,tag.album,tag.artist,tag.artist,path+"\\"+f[i])
                songss.append(song)
                artist_name=tag.albumartist
        if len(songss) == 0:
            return
        artists= db.getAll(con,"artist")
        for ar in artists:
            if ar.name == artist_name:
                artist_id = ar.id
                break

        if artist_id == -1:
            artist = en.artist("id",artist_name,0,"")
            x= db.addArtist(con,artist)
            artist_id = x.lastrowid

        album_name= self.most_common(albums_name)
        db.addAlbum(con,en.album(0,album_name,len(songss)))
        albums= db.getAll(con,"album")
        for al in albums:
            if al.name == album_name:
                for s in songss:
                    i =s.name.find("'")
                    ii = s.path.find("'")
                    if i == -1 and ii == -1 :        
                        s.album_name = album_name
                        s.album_id = al.id
                        db.addSong(con,s,artist_id)
                return



class SongListScreen(Screen):
    song_list = ObjectProperty(None)
    con = sqlite3.connect('musicly.db')
    ows=" " #obj_was_showen
    lg =" " #last get
    songs=[]
    bands=[]
    artists=[]
    albums=[]
    playlists=[]
    selection_index= 0
    song_index=-1
    playlist_index=-1
    obj_index_deletion=-1

    def addToScreen(self,arr):
        for s in arr:
            self.song_list.adapter.data.extend([s.name])
        self.song_list._trigger_reset_populate()
        

    #get all songs in DB
    def getAll(self,table_name):# table_name: song, playlist, band, artist, album
        self.song_list.adapter.data.clear()
        self.ows=table_name
        self.lg=table_name
        if table_name == "song":
            self.songs= db.getAll(self.con,table_name)
            self.addToScreen(self.songs)
            #self.play()
            #self.pause()
        
        elif table_name == "band":
            self.bands= db.getAll(self.con,table_name)
            self.addToScreen(self.bands)
        
        elif table_name == "artist":
            self.artists= db.getAll(self.con,table_name)
            self.addToScreen(self.artists)
        
        elif table_name == "playlist":
            self.playlists= db.getAll(self.con,table_name)
           # self.addToScreen(self.playlists)
            for s in self.playlists:
                self.song_list.adapter.data.extend([s.name+ " "*(35-len(s.name)) + "Tracks:"+str(s.numOfSongs)])
            self.song_list._trigger_reset_populate()
        
        elif table_name == "album":
            self.albums= db.getAll(self.con,table_name)
            self.addToScreen(self.albums)
    
    def getGeners(self):
        self.ows="gener"
        self.lg="gener"
        self.song_list.adapter.data.clear()
        geners = db.getGeners(self.con)
        for s in geners:
            self.song_list.adapter.data.extend([s])
        self.song_list._trigger_reset_populate()
		
    
    # use to every song in DB
    def play(self, x=-2):
        if self.song_list.adapter.selection and x == -2:
            self.selection_index = self.song_list.adapter.selection[0].index
        elif x != -2:
            if x >= len(self.songs):
                self.selection_index = 0
            elif x < 0:
                self.selection_index= len(self.songs) - 1
        elif x == - 2:
            self.selection_index = 0
        if len(self.songs) != 0:
            self.songs[self.selection_index].playSong()

    def pause(self):
        if len(self.songs) != 0:
            self.songs[self.selection_index].pauseSong()
    
    def unpause(self):
        self.songs[self.selection_index].unpauseSong()
    
    def stop(self):
        self.songs[self.selection_index].stopSong()
    
    def next(self):
        self.stop()
        self.selection_index += 1
        self.play(self.selection_index)
    
    def previous(self):
        self.stop()
        self.selection_index -= 1
        self.play(self.selection_index)
    
    #get songs of: playlist, band, artist, album
    def getSongs(self):
        index=-1
        ok = False
        if self.song_list.adapter.selection:
            index = self.song_list.adapter.selection[0].index
            self.lg= self.ows
            
        elif self.ows == " " or self.ows == "song":
            return
        self.song_list.adapter.data.clear()
        if index == -1:
            self.ows = self.lg 
            index = 0
        if self.ows == "band":
            self.songs = db.getSongs(self.con, "band", self.bands[index])
            self.addToScreen(self.songs)
        elif self.ows == "artist":
            self.songs = db.getSongs(self.con, "artist", self.artists[index])
            self.addToScreen(self.songs)
        elif self.ows == "playlist":
            self.songs = db.getSongs(self.con, "playlist", self.playlists[index])
            #self.addToScreen(self.songs)
            self.playlist_index_deletion=index
            self.song_list.adapter.data.extend(["Name:        "+self.playlists[index].name])
            self.song_list.adapter.data.extend(["Description: "+self.playlists[index].description])
            for s in self.songs:
                self.song_list.adapter.data.extend([s.name+ " "*(35-len(s.name)) + "Duration:"+self.toMin(s.length)])
            self.song_list._trigger_reset_populate()
        elif self.ows == "album":
            self.songs = db.getAlbumSongs(self.con, self.albums[index])
            self.addToScreen(self.songs)
        elif self.ows == "gener" and self.song_list.adapter.selection :
            self.songs = db.getSongsToGener(self.con, self.song_list.adapter.selection[0].text)
            self.addToScreen(self.songs)
        if self.selection_index != -1:
            self.ows ="song"
            #self.play()
            #self.pause()

    #order songs
    def spinner_clicked(self, value):
        self.song_list.adapter.data.clear()
        if value == "Name as":
            self.songs = db.ByName(self.songs,False)
        
        elif value == "Name de":
            self.songs = db.ByName(self.songs,True)
        
        elif value == "Album":
            self.songs = db.ByAlbum(self.songs)
        
        elif value == "Artist":
            self.songs = db.ByArtist(self.songs)
        
        elif value == "Gener":
            self.songs = db.ByGeners(self.songs)
        
        elif value == "Date":
            self.songs = db.ByReleaseDate(self.songs)
        
        self.addToScreen(self.songs)

    #add song to playlist
    def addSongToPlaylist(self):
        if self.song_index == -1:
            if self.song_list.adapter.selection and self.ows == "song":
                self.song_index = self.song_list.adapter.selection[0].index
            elif len(self.playlists) == 0:
                return
            else:
                return
            self.getAll("playlist")
        
        elif self.playlist_index == -1:
            if self.song_list.adapter.selection:
                self.playlist_index = self.song_list.adapter.selection[0].index
                self.addSongToPlaylist()
        
        elif self.song_index >= 0 and self.playlist_index >= 0:
            db.addSongToPlayList(self.con,self.songs[self.song_index],self.playlists[self.playlist_index])
            self.song_index = -1
            self.playlist_index= -1
            self.getAll("playlist")
    
    #delete song from playlist
    def deleteSongFromPlaylist(self):
        if self.song_index == -1 and (self.lg == "playlist" or self.ows != "song") :
            self.song_index = self.song_list.adapter.selection[0].index
        else:
            return
        db.removeSongFromPlaylist(self.con,self.songs[self.song_index-2],self.playlists[self.obj_index_deletion])
        self.obj_index_deletion=-1
        self.song_index=-1
        self.getAll("playlist")
    
    def deleteobj(self):
        index=-1
        if self.song_list.adapter.selection and ((self.lg != "song" and self.ows != "song") or (self.lg == "song" and self.ows == "song")):
            index = self.song_list.adapter.selection[0].index
            if self.ows == "song":
                db.deleteSong(self.con,self.songs[index])
                self.getAll("song")
            
            elif self.ows == "playlist":
                db.deletePlaylist(self.con,self.playlists[index])        
                self.getAll("playlist")
            
            elif self.ows == "album":
                db.deleteAlbum(self.con,self.albums[index])        
                self.getAll("album")
            
            elif self.ows == "artist":
                db.deleteArtist(self.con,self.artists[index])        
                self.getAll("artist")

    def toMin(self,x):
        remender= int(x)%60
        s = str(int(x/60)) + ":"
        if remender < 10:
            s+=str(0)+ str(remender)
        if remender == 0:
            s+= str(0)
        if remender > 10:
            s+= str(remender)
        return s 

    def songDetail(self):
        if self.song_list.adapter.selection and self.ows == "song":
            index = self.song_list.adapter.selection[0].index
            self.song_list.adapter.data.clear()
            self.song_list.adapter.data.extend(["Song: "+self.songs[index].name])
            self.song_list.adapter.data.extend(["Band: "+self.ListOneLine(self.songs[index].band_name)])
            self.song_list.adapter.data.extend(["Artist: "+self.ListOneLine(self.songs[index].artist_name)])
            self.song_list.adapter.data.extend(["Album: "+self.songs[index].album_name])
            self.song_list.adapter.data.extend(["Release Date: "+str(self.songs[index].releaseDate)])
            self.song_list.adapter.data.extend(["Genres: "+self.songs[index].geners])
            self.song_list._trigger_reset_populate()

    def ListOneLine(self,list):
        st=""
        if len(list)==0:
            return " "
        for i in range(len(list)):
            st+= list[i]
            if i!=len(list)-1:
                st += ","
        return st

class ProjectScreen(Screen):
    pass

class NewPlaylist(Screen):
    playlist_name = ObjectProperty(None)
    playlist_description = ObjectProperty(None)
    con = sqlite3.connect('musicly.db')
    def add_project_screen(self,playlist_name, playlist_description):
        name = playlist_name.text
        description = playlist_description.text
        playlist = en.playlist("id",name,description,0)
        db.addPlayList(self.con,playlist)

class NewArtist(Screen):
    artist_name = ObjectProperty(None)
    artist_date = ObjectProperty(None)
    con = sqlite3.connect('musicly.db')
    def add_artist_screen(self,artist_name, artist_date):
        name = artist_name.text
        date = artist_date.text
        artist = en.artist("id",name,0,date)
        db.addArtist(self.con,artist)
    
            




presentation = Builder.load_file("main.kv")

class ReportingApp(App):
    def build(self):
        screen_manager = ScreenManager()


        screen_manager.add_widget(HomeScreen(name="home_screen"))
        screen_manager.add_widget(SongListScreen(name="song_list_screen"))
        screen_manager.add_widget(NewPlaylist(name="new_playlist"))
        screen_manager.add_widget(NewArtist(name="new_artist"))
        return screen_manager
rr = ReportingApp()
rr.run()
