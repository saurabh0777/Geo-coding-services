Requested_id|unique_id|schemaName|tableName|filename|attributes|filelocation|type|partition_col|format|compression|col_without_partition|hdfs_location							
60ca20885a93013b239078f7|614447729|db2|address||{"email1":"tk41@gmail.com","firstname":"Tyler","lastname":"Keqmo","middlename":"Tyqler"}||ACID|NA|ORC|NA||/edx/us/lowes/secured/refined/db2/luw/address
60d9bf295a93013b23d009b8|356671282|db2|address||{"email1":"tammy@krshah.org","firstname":"Tamo","lastname":"Shah"}||ACID|NA|ORC|NA||/edx/us/lowes/secured/refined/db2/luw/address
60cc88aa5a93013b2399e8e9|65760796|sterling|yfs_order_header||{"customer_emailid":"jyates9@icloud.com","¸":"Julie1","customer_last_name":"tes","customer_phone_no":"86538555"}||ACID|NA|ORC|NA||/edx/us/lowes/secured/refined/oracle/sterling/yfs_order_header
60cdce3a5a93013b23a101b7|599088274|sterling|yfs_order_header||{"customer_emailid":"atrombino176@gmail.com","customer_first_name":"Aee","customer_last_name":"Trono","customer_phone_no":"908717093"}||ACID|NA|ORC|NA||/edx/us/lowes/secured/refined/oracle/sterling/yfs_order_header


out:
delete from db2.address where ( email1 = "tk41@gmail.com" and firstname = "Tyler" , lastname ="Keqmo", middlename = "Tyqler" ) or ( email1 = "tammy@krshah.org"  and firstname = "Tamo" , lastname = "Shah" );

