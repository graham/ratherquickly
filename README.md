# Rather Quickly

Structuring an application.

Demo Applications:

   Should be built with es6 so that things, actually work.

   Simple:
     - Basic Key Value Store or link manager.
     - Genie Object Wiki.

   Complex:
     - Reddit clone for companies (with a better economy system).
     - Meta/Block version of task manager, with syncing, and mobile.


Project 1, Basic Key Value Store:
 While not the best solution, storing keys in S3 makes this project even 
 easier. The app should provide a couple basic routes.

    1. Put    => update a key, if it already existed return true, if it's a 
                 new key return false.

    2. Get    => return the current state of the key, Null/None/Undefined all 
                 refer to the key not existing.

    3. Del    => remove the key from the database.

    4. Search => search for keys matching a string, should support offset.

 Applications are rooted in a folder called "functions", below that directory any folders
 containing a file called config.json are assumed to be paths that should be created.

 While custom routing __will__ be possible, for the duration of these demo applications
 we won't be using it.

 Directories with the config.json will likely also have a index.js (or whatever language)
 file. A directory containing a config.json doesn't restrict the developer from creating
 additional paths below that directory (they will also need a config.json in order to be
 added as a path.

## Something to keep in mind.

 RatherQuickly isn't designed to solve every problem, in fact, it's designed to be an
 easy way to publish code to url endpoints. Writing other tools that export and write
 files into the "functions" directory is encouraged, RatherQuickly should take care
 of the rest.

 You should assume that RatherQuickly will try it's best to not get in your way,
 and if it does file a request, and someone will fix it.

RatherQuickly.py the CLI helper:

 The python script that accompanies this module should allow you to quickly and
 easily create new applications. Once you've setup your .aws credentials you can quickly
 sync your current path state up to the server.

 There are however some basic routes you should watch out for. 

   - /_rq/rev  => This is the current revision and SCM that your project is using.
   - /_rq/list => This lists the currently available routes and their version.
   - /_rq/vers => This lists the most recent version of RatherQuickly used.

 