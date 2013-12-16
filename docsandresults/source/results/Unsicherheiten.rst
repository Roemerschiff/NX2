Der Einfluss von Messunsicherheiten auf die Auswertung
======================================================

Folgend gibt es Überlegungen zu den Fehlerquellen und deren Einfluss auf die Messungen mit dem NX2 bzw. auf die Auswertung. Dieser Text ist nicht in sich vollständig, sondern eine Ergänzung zu dem Kapitel „Technische Auswertung“ aus dem Buch „Lusoria Rhenana“ vom Verlag XYZ.


LOG
---
Das Log misst in guter Näherung zwischen 0,5 und 7kn linear, so dass eine Kalibrierung bei z.B. 3kn auch die anderen Geschwindigkeiten adequat beschreibt. Einzig bei Geschwindigkeit kleiner als 0,2-0,3kn reißt das Messsignal des Logs ab, da dass Rädchen dann nicht mehr schnell genug angeströmt wird.
Ruderschläge erzeugen natürlich nur in der Zugphase der Riemen Vortrieb, danach folgt 1-2 Sekunden eine Verlangsamung des Schiffes. Diese Spitzen bzw. Minima sind allerdings klein gegen die durschnittliche Geschwindigkeit und mitteln sich über 1-2 Minuten annähernd weg.
Die gleichmäßige Antriebskraft durch Ruderschläge ist subjektiv durch die Schlagmänner, die den Takt vorgeben und die übrigen Ruderer beeinflusst. Hin- und Rückweg einer Kalibrierungsfahrt wurden daher kurz hintereinander ohne eine Änderung der Sitzpositionen durchgeführt.
Eine systematische Beeinflussung, wenn z.B. die gleiche Schlagfrequenz durch mehr Kraftaufwand bei Gegenwind / Strömung angestrebt wird, ist nicht auzuschließen. Daher wurden mehrere Kalibrierungsfahrten mit unterschiedlichen Schlagmännern, Strecken und insbesondere bei milden Konditionen unternommen.
Es gibt einen zeitlichen Versatz der Geschwindigkeiten zum GPS (siehe dort), welcher aber aufgrund der gleichmäßigen Bewegung während der Kalibrierung keine Rolle spielt.
Ein unterschiedlicher Anströmwinkel des Logs ergibt sich nur bei variierender Beladung des Schiffes, da die Holzkonstruktion der Halterung mit einem "Schuh" versehen war, die nur eine Einbauposition über dem Bugsporn zulässt. Im Fall der Testwoche in 2012 wurde darüber hinaus das Log auch über Nacht die ganze Zeit fest montiert im Boot belassen.




Kontrolle der Log-Kalibration
-----------------------------
Um den Wert der oben berechneten Proportionalitätskonstanten zu überprüfen und sicher zu stellen, dass das Log linear reagiert, vergleichen wir nun die BSP und die SOG für einen wesentlich größeren Zeitraum. Dafür wählen wir alle Messpunkte aus, die folgende drei Bedingungen erfüllen:
Die BSP ist positiv, das Boot also in Fahrt. Für sehr kleine Geschwindigkeiten (unter 0,4 kn) reagiert das Log noch nicht, deshalb müssen diese Zeiten herausgefiltert werden.
Der Kompasskurs und die Bewegungsrichtung weichen um maximal 15° voneinander ab. Bei starken Drift, wie sie z.B. entstehen kann, wenn hart am Wind gesegelt wird, unterscheiden sich BSP und SOG schon dadurch, dass die SOG die gesamte Bewegung des Schiffes darstellt, das Log aber nur die Bewegungskomponente parallel zum Kiel misst.
Die Geschwindigkeit ändert sich nur wenig. Die SOG wird aus der Differenz der GPS Position momentan und wenige Sekunden zuvor berechnet. Diese Art der Differenzbildung führt zu einer Verzögerung von einigen Sekunden bevor eine veränderte Geschwindigkeit sich in der SOG niederschlägt.
Selbstverständlich enthält dieser Datensatz auch die Punkte aus der automatischen Logkalibration.




Windmesser
----------
Es ist zwischen Fehlern im gemessenen Windwinkel und der Windstärke zu unterscheiden. Der Windmesser selbst hat von Herstellerseite einige bekannte Offsets, welche in das NX2 Race zur Korrektur eingegeben wurde. Der größte Fehler beruht daher im Einbau des Windmessers. Dieser wurde jeden Tag neu befestigt und entlang des Vorderstevens ausgerichtet. Am Ende des Tages wurde der Einbau zudem kontrolliert, um nachträgliche Veränderungen zu bemerken bzw. ausschließen zu können. Dabei stellte sich allerdings heraus, dass die ganze Konstuktion sehr robust war, so dass hier eine Abweichung von mehr als 1-2° nicht zu erwarten ist.
Ein Stampfen des Schiffes oder eine Seitenlage beim Segeln, d.h. eine Veränderung der Drehachse des Windmessers, könnte zwar ebenfalls die Winkelmessung beeinflusst haben, doch zeigte sich die Konstruktion des Twin Fin Windmesser bereits bei Windgeschwindigkeiten von 1-2 kn als wenig anfällig, so dass dieser Fehler in der Größenordnung des vorherigen liegen sollte. Bei kleineren Windstärken oder sogar Windstille ist die Messung zudem ohne Bedeutung, da keine Segelwirkung erzielt wird.
Das Problem mit der Messung der Windstärke liegt weniger in dem Wert an sich als darin die Wirkung des Windes auf das Schiff zu erfassen. Besonders bei böigem Wind reagiert das Schiff zu träge, um die Bootsgeschwindigkeit direkt zu korrelieren. Bei Momentaufnahmen würde somit das Schiff fast still liegen, obwohl gerade ein starker Windstoß gemessen wird oder aber das Schiff hätte noch Vortrieb während der Wind (z.B.in der Nähe von Bäumen) plötzlich abreißt. Hierfür wurde der Wind mit einem Gauß-Profil geglättet, um eine durchschnittliche Windstärke über einen längeren Zeitraum zu erhalten. Dieses Profil ist verschoben, denn natürlich ist nur der Wind der vorangegangenen Sekunden maßgeblich für die momentane Geschwindigkeit des Schiffes.




Kompass
-------
Die Ausrichtung des Kompasses senkrecht zum Kiel stellte sicher, dass es keine einbaubedingten Offsets gab. Ebenso konnten an dieser Einbauposition Einflüsse durch Magnetfelder ausgeschlossen werden, da hier weder Eisen noch Batterien in der unmittelbaren Nähe vorhanden waren. Bei den Schiffen selbst handelt es sich zudem ja um Holzschiffe, in denen es nur an kritischen Stellen Eisennägel gibt. Die ausgewählten Stellen zur Befestigung des Kompasses besitzen selbst nur Holzverbindungen und ein wenig Abstand zu Eisennägeln. Die Besfestigung selbst wurde mit Klebeband realisiert.
Der schwierigste Teil der Kalibrierung ist wie üblich trotz Wind und Strömung mit dem Ruderantrieb einen gleichmäßigen Kreisradius einzuhalten. Im Rahmen der Messgenauigkeit wurden keine Korrekturen vorgenommen. Allerdings wurde auch bei einer Testfahrt auf einer Segeljacht mit dem NX2 bei guten Konditionen (geschütztes Hafenbecken, Motor mit konstanter Leistung) bei der ersten Kalibrierung keine nennenswerte Abweichung gefunden, so dass über die ganzen Messfahrten der Korrekturfaktor der aller ersten Kalibrierungsfahrt unter ebenso günstigen Bedingungen im Yachthafen in Wedel 2006 beibehalten wurde. Eine größere Abweichung zwischen den Gewässern der Testfahrten durch den Unterschied von geographischen zu magnetischen Nordpol gab es nicht.




GPS
---
Bei einer unmittelbaren Auswertung der Anzeigen Kompasskurs und GPS Kurs bleibt jedoch das Problem, dass es eine Zeitversetzung gibt. Die Kursrichtung durch zwei von einander getrennten GPS Positionsbestimmungen ist erst 2-3 s verzögert verfügbar. Dies ist auch beim Vergleich von Geschwindigkeit im Wasser durch das Log und Geschwindigkeit über Grund durch das GPS beobachtbar.
Das GPS ist außerdem träge. Um die Ungenauigkeit der Ortsbestimmungen (95% der Zeit sind diese auf 10 m genau) und gelegentlich Ausreißer zu kompensieren, wird über die vorangegangenen Geschwindigkeiten der letzten Sekunden gemittelt. Bei Geschwindigkeitsfahrten werden daher die absoluten Spitzenwerte am Ende eines einzelnen Riemenzuges nur im Log aufgezeichnet, während das GPS diese Ausreißer mit in die Durchschnittsgeschwindigkeit einrechnet. Die Abweichungen betragen aber normalerweise maximal 0,1 bis 0,2 kts




Server
------
Die Messdaten können aus dem Binärformat in ein CSV (column seperated values) Zwischenformat exportiert werden, welches sich mit jedem handelsüblichen Editor oder Tabellenkalkulationsprogramm öffnen lässt. Die Anzahl der gültigen Stellen ist hierbei jedoch von Herstellerseite vorgegeben. Während eigentlich alle Winkel und Geschwindigkeiten mit vier bzw. zwei Nachkommastellen mehr als ausreichend sind, ergeben sich bei der Positionsbestimmung durch das GPS mittels Longitude und Latitude Koordinaten mit sechs gültigen Ziffern leichte Sprünge wenn man den gefahrenen Kurs über eine Karte plottet. Dies führt beim Projezieren des gefahrenen Kurses auf elektronisches Kartenmaterial zu "Treppenstufen".




Polardiagramm
-------------
Wie bereits angedeutet wird bei der Erstellung eines Polardiagramms bei diversen Größen gemittelt, hierbei verschmiert das Ergebnis natürlich ein wenig. Angenommen es gäbe nur genau zwei Messpunkte in dem Intervall bei 3 kn und 150°, einer davon bei einer Windstärke von 3,5 kn mit 155° und der andere nur bei 2,5 kn mit 145° aufgezeichnet, dann wäre es nicht verwunderlich, wenn ersterer eine höhere Bootsgeschwindigkeit ergibt als letzterer. Auch wenn der Zusammenhang nicht linear ist, dürfte das mittlere Ergebnis in diesem Beispiel durchaus dicht am eigentlich gewünschten Wert von 3 kn mit 150° liegen. Aber was wenn nun einer der beiden Werte fehlt? Dann wird dieser Fehler für dieses eine Interval maximal. Aus diesem Grund gibt es zu jedem Polardiagramm noch ein Histogramm, welches die Anzahl der Messwerte wiedergibt und somit die Aussagekraft in dem jeweiligen Bin anzeigt.
Bei der Erstellung des Polardigrammes wird zudem vorher gefiltert. Da das Schiff aufgrund seines Gewichtes träge ist und das Segel optimal ausgerichtet werden muss, dauert es jeweils eine Weile bis das Schiff bei konstantem Kurs und konstanter Windrichtung und Windstärke seine optimale Endgeschwindigkeit erreicht. Es ist leicht einzusehen, dass man innerhalb dieser Zeit keine drastischen Änderungen haben möchte, sondern warten muss bis tatsächlich die Endgeschwindigkeit erreicht wurde. Ansonsten könnte der Skipper das Schiff aus voller Fahrt gegen die Strömung und gegen den Wind drehen und würde im ersten Moment noch Vortrieb messen bis das Schiff aufgestoppt hat und danach wieder zurückgetrieben wird. Ebenso könnte ein plötzlich aufkommender starker Wind bei einem treibenden Schiff im ersten Augenblick den Eindruck erwecken, dass dieses weiterhin treibt und gar nicht auf den Wind reagiert. Das ist mitnichten so und bereits das Schanzkleid bietet eine große Angriffsfläche.
Bevor das Polardiagramm auf eine Seite gefaltet wird, kann der Unterschied in den Schmetterlingsflügeln auf Back- und Steuerbordseite als Qualität der Messwerte und der Filterung angesehen werden. Mit genügend Messpunkten und starker Filterung müssten beide Seiten identisch sein, da auch die Schiffe in sehr guter Näherung symmetrisch gebaut sind.




Drift
-----
Bei achterlichem Wind und ohne Strömung gibt es keinen seitlichen Versatz, daher ist diese Windstellung ein Maß für die Genauigkeit der Messung.
Das NX2 ist vergesslich, d.h. ohne einen angeschlossenen Computer mit Festplatte werden die aktuellen Daten aufbereitet und kurz im Display angezeigt. Dabei ist davon auszugehen, dass die Trägheit des GPS, Geschwindigkeiten erst nach einer zweiten Ortsbestimmung, also mit 3-4 Sekunden Verzögerung, auszurechnen, eine Ungenauigkeit bei schnell und eng gefahrenen Kurven darstellt, denn die Log und Kompassdaten sind weniger alt.




Ruderschlagliste
----------------
Der Protokollant wurde häufiger gewechselt, z.T. war auch niemand verfügbar, so dass die Liste von der Technik nebenher geführt wurde. Es konnte bereits während der Fahrt beobachtet werden, dass die Qualität sehr stark personenbezogen war. Bei längeren eintönigen Strecken, aber auch bei waghalsigen Manövern kam es immer wieder vor, dass nach einer vollen Minute zu spät in die nächste Zeile gewechselt wurde. Außerdem wurden Manöver nicht immer kleinteilig notiert. Bei der parallelen Führung durch die Technik musste zudem teilweise im Kopf mitgezählt werden und nachgetragen werden, wenn gerade andere Handgriffe zu tun waren.
Auch wenn es theoretisch möglich ist kurze Geschwindigkeitszuwachse im Wasser, die durch das Log gemessen werden, als Zugphase beim Rudern zu identifizieren, wurde auf einen solchen Vergleich verzichtet. Die Segelstart-/endzeiten sollten hingegen akkurat sein, da sie auch im Log des NX2 verzeichnet wurden. Ebenso wurde bei Geschwindigkeitsfahrten auf eine höhere Genauigkeit geachtet. Um Manöver für eine spätere Auswertung wiederzufinden, ist keine sekundengenaue Übersicht erforderlich.




Testgewässer
------------
Die Versuchsgewässer waren in ihren Eigenschaften unterschiedlich, was insbesondere einen Vergleich der beiden Navis Lusoriae erschwert. Während bereits 2005 und 2006 mit der Regina auf der Naab und der Donau in Regensburg getestet wurde, waren die Altrheinarme in Wörth am Rhein und Germersheim bei der Rhenana 2011 und 2012 eher langsam fließende Gewässer. Insbesondere die Segelstrecken waren auf der Donau durch die Strömung, den Wind, die Flussufer und die Berufsschifffahrt vorgegeben, während bei den späteren Versuchsreihen zumindest etwas ausgedehntere Flächen zum Manövrieren und insbesondere mehrere Segeltage mit unterschiedlichen Windverhältnissen zur Verfügung standen.




Strömungskorrektur
------------------
Auch wenn die Korrekturen der Strömungssimulation grundsätzlich in die richtige Richtung zielen sollten, ergibt sich hierdurch dennoch eine weitere Fehlerquelle, da das Modell abhängig von diversen Parametern und Annahmen ist, sodass nicht von einer 100% Übereinstimmung mit den tatsächlichen Strömungen im Testgebiet ausgegangen werden kann.
Bei der Victoria 2008 fanden die Testfahrten zum größten Teil auf dem Domsee in Ratzeburg statt, wobei auch einzelne längere Fahrten auf den Ratzeburger See unternommen wurden. Dieses Gewässer war am besten für die Erprobung eines römischen Flusskriegsschiffes geeignet, da es quasi keine Strömung gab und die Einschränkungen durch nahe Ufer und andere Wasserfahrzeuge die meiste Zeit vernachlässigt werden konnten.
