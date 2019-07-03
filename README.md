# Nimbus Cloud Backup
Application that allows users
to backup the contents of a specified local directory using a cloud service.
Made of backup server (bs folder) central server (cs folder) and client(user.py) in python using tcp/udp.

To perform any cloud backup operation the user first needs to authenticate itself. For
this, the user application establishes a TCP session with the CS, which has a wellknown URL, providing the user identity
and a password (composed of 8 alphanumerical characters, restricted to letters and
numbers). The CS will confirm the authentication.
The user can then decide to perform one of the operations:
1 – Register as a new user.
2 – Request the backup of a selected local directory.
3 – List the previously stored directories and files.
4 – Retrieve a previously backed up directory.
5 – Delete the backup for a selected directory.
6 – Delete the registration as a user.
The directories to be backed up should be contained in the current directory from where
the user program was invoked, and they should not contain subdirectories. File and
directory names should not contain spaces and should have less than 20 characters. In
the current directory there should be at most 20 directories, each one with a maximum
of 20 files.
When requesting the backup of a local directory the user application sends to the CS a
backup request message indicating: the directory name and the number and list of files
to be backed up (with name, date, time, size).

To retrieve the files from a previous backup, the user application contacts the CS,
sending the name of the directory being retrieved. The CS checks which BS contains the
backup and returns the corresponding IP and TCP port. The user application then closes
the TCP connection with the CS and automatically establishes a new TCP session with
the BS, to retrieve the files, after authentication.

![Alt Text](https://i.ibb.co/m5LBt8q/image-2019-07-03-20-00-05.png)

