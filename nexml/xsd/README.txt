This directory and its subfolders contains the latest version of the nexml schema
from the subversion repository. The schema is designed following the 'Venetian
Blinds' design pattern. With this design approach we disassemble the problem 
into individual components. Instead of creating element declarations, we create type 
definitions.

This design has:

    * maximized reuse
    * maximized the potential to hide (localize) namespaces.

The Venetian Blind design espouses these guidelines:

    * Design your schema to maximize the potential for hiding (localizing) namespace complexities.
    * Use elementFormDefault to act as a switch for controlling namespace exposure - if you want element namespaces exposed in instance documents, simply turn the elementFormDefault switch to "on" (i.e, set elementFormDefault= "qualified"); if you don't want element namespaces exposed in instance documents, simply turn the elementFormDefault switch to "off" (i.e., set elementFormDefault="unqualified").
    * Design your schema to maximize reuse.
    * Use type definitions as the main form of component reuse.
    * Nest element declarations within type definitions.
    
For more about this (and other) schema design patterns and best practices, visit
http://www.xfront.com/GlobalVersusLocal.html#ThirdDesign
