# How to do stuff around VMCKV2
After deployment there will be an admin user and **ONLY** that person can:
* add **NEW COURSES**
* add **NEW TEACHING ASSISNTATS** for a course

## How to add a new Course
Go to the url where the server is deployed (v2.vmchecker.cs.pub.ro is the public link used by the
Faculty of Automatic Control and Computer Science). At the end of the url you need to add */admin*
-- this is the interface for the administrator.

For a fresh deployment only the admin user will have the right to enter here.

Click the **+** sign from the right-side of the Course, complete the Course information and then
click **OK**. If everything is ok, you should see a new course when you enter the normal link -- without
the admin interface.

## How to add a new teaching assistant
For this the *admin* user should go to the *Course* page and select the
The TAS has the following **permissions**:
* add/change/remove assignments for the course where they were added as TAS
* add/change/remove submissions for the course where they were added as TAS

## Add new superusers
You can do this by:
* Go to *Users* from the admin interface
* Select a user
* Check the box for superuser
* ATTENTION: The number of superusers should be kept at a minimum!!!
* ATTENTION2: The superuser can add/remove/delete everything you can as an admin!!!
