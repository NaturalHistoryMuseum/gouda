javac -cp ..\zxing\core-3.1.0.jar;..\zxing\javase-3.1.0.jar -Xlint:unchecked decode_data_matrix.java
jar cvf decode_data_matrix.jar *class
