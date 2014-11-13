This folder contains zxing jars

    cd ~/build
    git pull zxing

    brew install maven

Download and install latest 1.7.x jdk

Following [zxing instructions](https://github.com/zxing/zxing/wiki/Getting-Started-Developing).

    cd ~/build/zxing/core

A [tip](http://stackoverflow.com/questions/18813828/why-maven-use-jdk-1-6-but-my-java-version-is-1-7):

    export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.7.0_67.jdk/Contents/Home/
    mvn -DskipTests clean package

    cd ../javase
    mvn clean package
