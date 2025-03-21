package com.example.port_health;

import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class DoctorActivity extends AppCompatActivity {
    private ListView listViewPatients;
    private TextView textViewAppointments;
    private EditText editTextNewAppointment;
    private Button buttonSubmitAppointment;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_doctor);

        listViewPatients = findViewById(R.id.listViewPatients);
        textViewAppointments = findViewById(R.id.textViewAppointments);
        editTextNewAppointment = findViewById(R.id.editTextNewAppointment);
        buttonSubmitAppointment = findViewById(R.id.buttonSubmitAppointment);

        // Hardcoded list of patients
        String[] patients = {"John Doe", "Jane Smith", "Michael Johnson"};

        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, patients);
        listViewPatients.setAdapter(adapter);

        listViewPatients.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                // Hardcoded past appointment for the selected patient
                String pastAppointment = "Past appointment with " + patients[position] + " on 01/15/2025\n";
                textViewAppointments.setText(pastAppointment);
            }
        });

        buttonSubmitAppointment.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String newAppointment = editTextNewAppointment.getText().toString().trim();
                if (!newAppointment.isEmpty()) {
                    String currentText = textViewAppointments.getText().toString();
                    textViewAppointments.setText(currentText + "\nNew appointment: " + newAppointment);
                    editTextNewAppointment.setText("");
                }
            }
        });
    }
}