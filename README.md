2019-12-27/Stefan Blaschke

# homie
Rasperry pi project for temperature, voltage and rpm ...

Die Hauptdatei ist "homie.py" welche mit "index.html" verknüpft ist.
Die "index.html" triggert mit dem Skript
  <script>
   function updateTemperature1()
   {
      fetch( "/getdyntemp1" )
         .then( response => {
            if( !response.ok )
               throw new Error( "fetch failed" ) ;
            return response.json() ;
         } )
         .then( json => document.querySelector("#getdyntemp1").textContent = json.getdyntemp1 )
   }
   updateTemperature1() ;
   setInterval( updateTemperature1, 1000 ) ;
  </script>
in regelmäßigen Abständen das Python Programm "homie.py" an und liest z. B. die Temperaturwerte der beiden Temperatursensoren aus bzw. auch den Spannungswert.

Im weiteren Schritt soll nun die Drehzahl eines Benzinmotors mittels eine Hall-Sensors gemessen und auf der Homepage "index.html" dargestellt werden.

Das aktuelle "Problem" ist, dass die Ermittlung der Drehzahl "allein" (rpm_standalone.py) grundsätzlich funktioniert, jedoch mit dem parallel arbeitenden Prozess von "homie.py" nicht wirklich zurecht kommt.
Nach Informationen in einschlägigen Foren liegt das Geheimnis in:

Zitat Start
  "wenn du Drehzahl permanent (= in einer Endlosschleife) gemessen wird, dann kannst du das nicht im gleichen Prozess machen in dem den Flask Server läuft, weil die Endlosschleife den Server blockiert.
  Was z.B. geht ist, die Drehzahlmessung in einen eigenen Prozess auslagern, der dann über eine Queue mit dem Server-Prozess kommuniziert:"
  ----------
  "der entscheidende Punkt ist die Queue, über die die Messung mit der Route in Flask "kommuniziert".
  Die Queue musst du halt an passender Stelle in deiner Klasse einbauen und das Messergebnis da rein schieben.
  Des Weiteren musst du in dem separatem Prozess, der via Multiprocessing gestartet wird, die Methode deiner Klasse aufrufen,
  die die Endlosmessung startet. Grundsätzlich du brauchst halt zwei Prozesse und irgendwas, über das die Prozesse kommunizieren.
  Das kann, wenn die Prozesse einzeln gestartet werden, auch ein Socket oder eine Named Pipe oder eine Datei oder eine Datenbank oder ... sein."
Zitat Ende

homie.py stellt einen ersten Versuch der Kombination aus dem File "rpm_standalone.py" dar - funktioniert aber so natürlich nicht
