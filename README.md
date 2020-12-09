# use

These are some experiments being conducted by Jess Ogden, Shawn Walker and Ed
Summers to examine the use of web archives on the web. We are looking for the
traces of web archives in a web archive (CommonCrawl). If that sounds
confusingly meta then you are understanding correctly :)

At the moment `load.py` downloads all the WAT files for a given CommonCrawl
snapshot and looks for links to known web archives, and writes out a CSV of
data about those links including:

* source_url: the url linking to the web archive
* source_host: the host name of the source url 
* archive_url: the URL of a web archive resource
* archive_service: the archive service, e.g. InternetArchive, ArchiveToday, etc
* link_text: the text of the hypertext link
* path: the CSS selector path to the link in the source page
* link_count: the total number of hyperlinks on the page
* warc: the CommonCrawl WARC file where the response is stored
* offset: the byte offset into the WARC file where the response is
* inflated_length: the inflated length of the response
* deflated_length: the compressed length of the response

## Install

    git clone https://github.com/edsu/use.git
    cd use
    pip install -r requirements.txt

## Run

You give `load.py` the snapshot ID of a [CommonCrawl] dataset. For
example:

    ./load.py CC-MAIN-2020-45

Wait a looooong time. Look at load.log to see what's happening then when
it's done you will have a CSV file:

    CC-MAIN-2020-45.csv

[CommonCrawl]: https://commoncrawl.org/
[CommonCrawl dataset]: https://commoncrawl.org/the-data/get-started/
