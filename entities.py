#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pygame import mixer
import mutagen.mp3


# In[2]:


class album:
    def __init__(self, id, title, numOfSongs):
        self.id = id
        self.name =title
        self.numOfSongs =numOfSongs
    def view(self):
        print(self.name,end=" "* (35-len(self.name)))
        print("Tracks: "+str(self.numOfSongs))


# In[3]:


class artist:
    def __init__(self, id, name, band_id , dateOfBirth):
        self.id = id
        self.name =name
        self.band_id =band_id
        self.dateOfBirth=dateOfBirth
    def view(self):
        print(self.name)


# In[4]:


class band:
    def __init__(self, id, name):
        self.id = id
        self.name =name
    def view(self):
        print(self.name)


# In[5]:


class playlist:
    def __init__(self, id, name, description, numOfSongs):
        self.id = id
        self.name =name
        self.description =description
        self.numOfSongs=numOfSongs
    def view(self):
        print(self.name,end=" "*(35-len(self.name)))
        print("Tracks: "+str(self.numOfSongs))


# In[6]:


class song:
    def __init__(self, id, name, releaseDate, geners, lyrics, length, album_id, album_name, artist_name, band_name, path):
        self.id=id
        self.name=name
        self.releaseDate=releaseDate
        self.geners=geners
        self.lyrics=lyrics
        self.length=length
        self.album_id=album_id
        self.album_name=album_name
        self.artist_name=artist_name
        self.band_name=band_name
        self.path=path
    def view(self):
        print("Song: "+self.name)
        print("Band: ",end="")
        printListOneLine(self.band_name)
        print("artist: ",end="")
        printListOneLine(self.artist_name)
        print("Album: "+self.album_name)
        print("Release date: "+str(self.releaseDate))
        print("Geners: "+self.geners)
    def playSong(self):
        song_file = self.path
        mp3 = mutagen.mp3.MP3(song_file)
        mixer.init(frequency=mp3.info.sample_rate)
        #print("frequency= "+str(mp3.info.sample_rate))
        mixer.music.load( song_file)
        mixer.music.play()
    def pauseSong(self):
        mixer.music.pause()
    def unpauseSong(self):
        mixer.music.unpause()
    def stopSong(self):
        if mixer.music.get_busy():
            mixer.music.stop()
            mixer.quit()


# In[7]:


def printListOneLine(list):
    st=""
    if len(list)==0:
        return " "
    for i in range(len(list)):
        st+= list[i]
        if i!=len(list)-1:
            st += ","
    return st


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




