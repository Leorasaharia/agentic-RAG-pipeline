plugins {
    java
    application
}

repositories {
    mavenCentral()
}

dependencies {
    // Manually include JavaFX for Windows (Bypassing the plugin's ARM processor crash)
    val javafxVersion = "17.0.6"
    implementation("org.openjfx:javafx-base:$javafxVersion:win")
    implementation("org.openjfx:javafx-controls:$javafxVersion:win")
    implementation("org.openjfx:javafx-fxml:$javafxVersion:win")
    implementation("org.openjfx:javafx-graphics:$javafxVersion:win")

    // Original dependencies
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    // Note: To use websockets realistically in Java, we add okhttp
    implementation("com.squareup.okhttp3:okhttp:4.11.0")
}

application {
    mainClass.set("com.agenticrag.desktop.Launcher")
}
