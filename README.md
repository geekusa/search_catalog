# Search Catalog

The intent of this app is to provide a simple interface for sharing knowledge in Splunk through editing a simple CSV file, the app can generate a set of standard dashboards and navigation. 

Available at:

[Github](https://github.com/geekusa/search_catalog)

Version: 1.1.1

## Description and Use-cases

Have you ever wanted a centralized location to direct users to so they can find what they need? Example: What special index do we store our firewall data? This app provides a simple interface for both administrators (to catalog data locations) and users (to find the data they need).

Depending on how Splunk is managed, finding data for a new (or even experienced) user can be challenging. The primary use-case of this app is for a Splunk adminstrator to be able to easily catalog (using a CSV file) where specific types of data (that an end user may have interest in) would be found on the given system and provide the end user an interface to quickly find this data (using Splunk’s built in menu system). Even though there exists the CIM, not all data is CIM compatible, nor is a user necessarily familiar with CIM. This can be especially helpful as new data types become available in Splunk that are not complying with CIM.

## How to use

### Adminstrator

The app comes with an example CSV lookup file with sections, subsections and searches that should be universal. Using the built-in dashboard to add searches, an administrator can fill the catalog with the necessary content for the users. The CSV can also be edited directly or the app contains links to open the file in the Lookup File Editor app (https://splunkbase.splunk.com/app/1724/ requires 2.x), especially useful if searches need to be deleted. While it is not required, it is recommended to fill out the Notes section of each search so that both the generated dashboard will give some helpful context and a user may find the search based on keywords in the notes (using the search dashboard called “Not Sure Where to Look?"). The administrator should either copy the example CSV found in the samples directory to the lookups directory or use the add searches dashboard to create the file. 

Once the lookup/CSV file has been populated with searches, the app has a custom command to generate menus and dashboards based on the searches given (“Generate Dashboards”). Each search is given it’s own dashboard with notes, events, and some basic info and statistics of it’s primary fields. There are also links to open the search up in the normal search window (in the regular Search app not the Search Catalog) from the dashboard as well as a time range picker. 

Each generated dashboard includes a panel titled “Most Populated Fields”. If an admin wants to filter specific fields out of this (i.e. date\_\*) the most\_populated\_filter.csv file must be created and filled. Similar to the search\_catalog.csv the app contains an example most\_populated\_filter.csv, and again the administrator should either copy the example CSV found in the samples directory to the lookups directory or use the add searches dashboard to create the file.

### End User

From the Welcome screen a user is introduced to the number of searches that exist in the search catalog along with an idea of how those searches are dispersed. The user is given instructions to browse through the Search Catalog’s menus, search or see what are the latest searches that have been added. 

### Support
Support will be provided through Splunkbase (click on Contact Developer) or Splunk Answers or [submit an issue in Github](https://github.com/geekusa/search_catalog/issues/new). Expected responses will depend on issue and as time permits, but every attempt will be made to fix within 2 weeks. 

### Documentation
This README file constitutes the documenation for the app and will be kept upto date on [Github](https://github.com/geekusa/search_catalog/blob/master/README.md) as well as on the Splunkbase page.

### Release Notes
Fixed Most Populated Fields panel to not max out on quantity of distinct values.
