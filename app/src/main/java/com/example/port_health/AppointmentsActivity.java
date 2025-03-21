package com.example.port_health;

import android.os.Bundle;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class AppointmentsActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_appointments);

        TextView textViewAppointments = findViewById(R.id.textViewAppointments);

        // Hardcoded past appointments
        String appointments = "1. Appointment with Dr. Smith on 01/15/2025\n" +
                              "2. Appointment with Dr. Johnson on 02/20/2025";

        textViewAppointments.setText(appointments);
    }
}