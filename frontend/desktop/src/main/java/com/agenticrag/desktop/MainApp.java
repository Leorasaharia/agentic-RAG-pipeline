package com.agenticrag.desktop;

import javafx.application.Application;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.layout.VBox;
import javafx.scene.text.Font;
import javafx.stage.Stage;

public class MainApp extends Application {

    @Override
    public void start(Stage primaryStage) {
        primaryStage.setTitle("AgenticRAG Desktop App (JavaFX)");

        Label titleLabel = new Label("AgenticRAG Desktop Console");
        titleLabel.setFont(new Font("Arial", 24));

        Label descLabel = new Label("This represents the optional Java desktop UI client.\nFull streaming chat features would be developed here.");
        descLabel.setAlignment(Pos.CENTER);

        Button startButton = new Button("Launch Connection");
        startButton.setOnAction(e -> {
            System.out.println("Initiating connection... (Mock)");
        });

        VBox root = new VBox(20, titleLabel, descLabel, startButton);
        root.setAlignment(Pos.CENTER);

        Scene scene = new Scene(root, 600, 400);
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
