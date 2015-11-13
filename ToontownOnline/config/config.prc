# Toontown Client Settings

# Window title, filenames, and paths
window-title Toontown

cursor-filename phase_3/etc/toonmono.cur
icon-filename phase_3/etc/icon.ico
model-path resources

# Gameserver IP and Server Version that must be kept in sync #with Astron
game-server localhost
server-version sv0.0.0.1-dev

# Force SSL and the Astron port
server-force-ssl 0
server-port 7198

# Graphical Settings
load-display pandagl

# DC Files
dc-file astron/toon.dc
dc-file astron/otp.dc

# Audio library name and the Account DB file
audio-library-name p3fmod_audio
accountdb-local-file astron/database/account-db.db

# No account server
#account-server-endpoint https://www.dummy.com/api/account

default-model-extension .bam

# In-game Features
cog-thief-ortho 0
show-total-population #t
want-mat-all-tailors #t
want-tailor-jellybeans #t
estate-day-night #t
want-karts #f
want-pets #f
want-news-page #f
want-news-tab #f
want-housing #f
want-dev #f
force-holiday-decorations #f
want-old-fireworks #t
want-instant-parties #t
