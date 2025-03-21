package com.example.port_health;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Връзка към бутоните от XML
        Button btnAppointments = findViewById(R.id.btnAppointments);
        Button btnPrescriptions = findViewById(R.id.btnPrescriptions);
        Button btnMedicalHistory = findViewById(R.id.btnMedicalHistory);
        Button btnChat = findViewById(R.id.btnChat);
        Button btnInfo = findViewById(R.id.btnInfo);

        // Стартиране на съответните Activity-та
        btnAppointments.setOnClickListener(v -> startActivity(new Intent(this, AppointmentsActivity.class)));
        btnPrescriptions.setOnClickListener(v -> startActivity(new Intent(this, PrescriptionsActivity.class)));
        btnMedicalHistory.setOnClickListener(v -> startActivity(new Intent(this, MedicalHistoryActivity.class)));
        btnChat.setOnClickListener(v -> startActivity(new Intent(this, ChatActivity.class)));
        btnInfo.setOnClickListener(v -> startActivity(new Intent(this, InfoActivity.class)));
    }
}
