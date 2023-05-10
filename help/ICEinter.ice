module app {
 
 class Song {
     string titre;
     string artist;
     string audio;
 };
    
 sequence<Song> songs;
 
 interface MusicServer {
     bool upload(Song s);
     bool delete(string titre);
     bool modify(Song s);
     songs findByName(string titre);
     songs findByArtist(string artist);
     songs getAll();
    bool play(Song s);
    bool pause(int id);
    bool resume(int id);
    bool stop(int id);
 };
 
 interface MusicClient {
     void ping();
     MusicServer getServer(string ip);
 };

};

