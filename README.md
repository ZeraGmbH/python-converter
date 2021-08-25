# PythonConverter
Zera value database to xml converter

This application takes an sqlite3 database as Input and converts it into an 
xml file. The The database has to follow the structure described in 
the topic sql structure.

The output depends on the used engine. Two Engines are shipped in this pkg.
1. MTVisMain.py
Creates MTVis Main.xml file from mt310s2 database
2. MTVisRes.py
Creates MTVis Result.xml file from mt310s2 database

## Install 

### qtCreator

Follow  the instructions described in "Run from qtCreator"
Also make sure to add the installation directory to PYTHONPATH in your run configuration, if you are using this project
in combination with a C++ project.

The best way to make sure the pythonpath is properly accounted for is to add it to your kit.

### terminal

1. call: python setup.py sdist
2. call: ython -m pip install dist/pythonconverter_pkg-0.0.1.tar.gz --prefix=${CMAKE_INSTALL_PREFIX}

Replace ${CMAKE_INSTALL_PREFIX} with a paht of your choice. Not using --prefix is equal to
--prefix=/usr

## How to use

Your can use this pkg from command line or implement it in C++.

### Run from command line

In commad line just call:

```
ZeraConverter -i <sqlitefile>.db -o <file>.xml --session=<sessionName>
```

### Run from qtCreator

1. Import cmake Project
2. Go to Projects->Run
3. Add ZeraConverter as executable in run configuration

You can edit, build, run and install this project just like a C project now.

Attention: The cmake is only wrapping around setup.py.

### Implement in C++

In c++ you can use CppInterface to bind the conversion functions to your programm.
It is recommendet to use the Zera PythonScriptingInterface to do that.

For more information visit: https://github.com/ZeraGmbH/PythonScriptingInterface

Call the functions in following order:
```
1. setInputPath(<sqlitefile>.db)
2. setOutputPath(<file>.xml)
3. setSession(<sessionName>)
4. convert()
```
If the input database or engine is not existing nothing will happen and ```convert()``` will return false.
If the engines api does not fit, the pythonscript will hang in debugging mode or return with an exception 
in normal execution. You will not be able to catch the python exception. However it should not crash 
the C++ application either. Only the terminal will tell you what happened in this case.

## Error Flags

Errors are stored in __errorRegister and __userScriptErrors. 

errorRegister contains genral programm errors and warnings.
userScriptErrors contains userScript specific errors. Their 
meaning might vary depending on the script(engine).

Make sure to use only the first 16 bit in each register.

errorRegister
   - 0: all good
- errors:
   - 1: userScript error
   - 2: open input database error
   - 4: open output database error
   - 8: database read error
   - 16: manipulate set error
   - 32: write output database error
   - 64: not used
   - 128: not used
- warnings:
   - 256: input database close warning
   - 512: invalid parameter syntax warning
   - 1024: session empty or does not exist
    ....

MTVisRes userScript

userScriptErrors
  - 0: all good
- if error:
  - 1: critical error (not used)
- details and warnigs:
  - 2: one or more transactions not exported warning


Zeraconverter.py and CppInterface.convert() returns: 

|16 bit| 16 bit |
|------|--------|
|userScriptErrors|errorRegister|

## Write your custom conversion engine

comming soon

## sql structure

```
CREATE TABLE components (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, component_name varchar(255));
CREATE TABLE entities (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, entity_name varchar(255));
CREATE TABLE sessions (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, session_name varchar(255) NOT NULL);
CREATE TABLE transactions (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, sessionid integer(10) NOT NULL, transaction_name varchar(255), contentset_names varchar(255), guicontext_name varchar(255), start_time timestamp, stop_time timestamp, FOREIGN KEY(sessionid) REFERENCES sessions(id));
CREATE TABLE transactions_valuemap (transactionsid integer(10) NOT NULL, valueid integer(10) NOT NULL, PRIMARY KEY (transactionsid, valueid), FOREIGN KEY(valueid) REFERENCES valuemap(id), FOREIGN KEY(transactionsid) REFERENCES transactions(id));
CREATE TABLE sessions_valuemap (sessionsid integer(10) NOT NULL, valueid integer(10) NOT NULL, PRIMARY KEY (sessionsid, valueid), FOREIGN KEY(valueid) REFERENCES valuemap(id), FOREIGN KEY(sessionsid) REFERENCES sessions(id));
CREATE TABLE valuemap (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, value_timestamp timestamp, component_value numeric(19, 0), componentid integer(10), entityiesid integer(10), FOREIGN KEY(entityiesid) REFERENCES entities(id), FOREIGN KEY(componentid) REFERENCES components(id));
```

## Test

This project provides a sample database test/test.db. Calling ZeraConverter with -d this database will be converted to test/out.xml.
Alle genrated files are consideret in .gitignore. So do not worry about those, if contributing to the project.

