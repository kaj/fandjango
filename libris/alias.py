# -*- coding: utf-8 -*-
def aliases(name, *alias):
    return [(a,name) for a in alias]

ALIASES = dict(
    aliases(u'Abel Romero', u'A. Romero') +
    aliases(u'Alan Gordon', u'Al Gordon', u'Gordon') +
    aliases(u'Alex Saviuk', u'Saviuk') +
    aliases(u'Alf Woxnerud', u'Wox') +
    aliases(u'Alfredo P. Alcala', u'Alfred P. Alcala', u'Red Alcala') +
    aliases(u'Alfredo Castelli', u'Castelli') +
    aliases(u'Anders Eklund', u'A. Eklund') +
    aliases(u'André Franquin', u'Franquin') +  
    aliases(u'Anette Salmelin', u'A. Salmelin') +
    aliases(u'Ann Schwenke', u'A. Schwenke') +
    aliases(u'Anniqa Tjernlund', u'A. Tjernlund') +
    aliases(u'Bengt Sahlberg', u'B. Sahlberg') +
    aliases(u'Bertil Wilhelmsson', u'B. Wilhelmsson', u'Wilhelmsson',
            u'Bertil W-son') +
    aliases(u'Birgit Lundborg', u'Biggan Lundborg', u'B. Lundborg') +
    aliases(u'Björn Ihrstedt', u'B. Ihrstedt', u'B Ihrstedt') +
    aliases(u'Carlos Cruz', u'Carloz Cruz', u'C. Cruz', u'Cruz') +
    aliases(u'Claes Reimerthi', u'C. Reimerthi', u'Reimerthi') +
    aliases(u'César Spadari', u'Cèsar Spadari', u'Cesàr Spadari', u'Cesár Spadari', u'Cesar Spadari', u'C. Spadari', u'Spadari') +  
    aliases(u'Dag R. Frognes', u'Dag Frognes') +
    aliases(u'Dai Darell', u'Darell') +
    aliases(u'Donne Avenell', u'Don Avenell', u'D. Avenell', u'Avenell') +
    aliases(u'Eirik Ildahl', u'Eiric Ildahl') +
    aliases(u'Eugenio Mattozzi', u'E. Mattozzi') +
    aliases(u'Falco Pellerin', u'F. Pellerin', u'Terje Nordberg') +
    aliases(u'Ferdinando Tacconi', u'Fernanino Tacconi', u'Tacconi') +
    aliases(u'Fred Fredericks', u'Fredericks') +
    aliases(u'Georges Bessis', u'Georges Bess', u'G. Bess') +
    aliases(u'Germano Ferri', u'Ferri') +
    aliases(u'Grzegorz Rosinski', u'G. Rosinski', u'Rosinski') +
    aliases(u'Göran Semb', u'Semb') +
    aliases(u'Hans Jonsson', u'Hans Jonson', u'Hasse Jonsson', u'H. Jonsson', u'H Jonsson') +
    aliases(u'Hans Lindahl', u'Hasse Lindahl', u'H. Lindahl', u'Lindahl') +
    aliases(u'Heiner Bade', u'Helmer Bade', u'H. Bade', u'H Bade', u'H. Baade', u'Bade') + 
    aliases(u'Henrik Brandendorff', u'H. Brandendorff', u'Henrik Nilsson') +
    aliases(u'Idi Kharelli', u'Kharelli') +
    aliases(u'Iréne Gasc', u'Irene Gasc') +
    aliases(u'Iván Boix', u'Ivàn Boix', u'Ivan Boix') +
    aliases(u'Jaime Vallvé', u'J. Vallvé', u'Vallvé') +
    aliases(u'Janne Lundström', u'Jan Lundström', u'J. Lundström', u'Lundström') +
    aliases(u'Jean Giraud', u'J. Giraud', u'Giraud') +
    aliases(u'Jean Van Hamme', u'J. Van Hamme', u'J Van Hamme', u'Van Hamme') +
    aliases(u'Jean-Michel Charlier', u'J-M. Charlier', u'J-M Charlier', u'Charlier') +
    aliases(u'Jean-Yves Mitton', u'J-Y Mitton', u'Mitton') +
    aliases(u'Karl-Aage Schwartzkopf', u'K.-A. Schwartzkopf', u'K-A Schwartzkopf') +
    aliases(u'Kari Leppänen', u'Kari T. Leppänen', u'Kari T Leppänen', u'Kari Leppänän', u'Kari Läppänen', u'Kari Läppenen', u'K. Leppänen', u'Leppänen') +  
    aliases(u'Karin Bergh', u'K. Bergh') +
    aliases(u'Knut Westad', u'K. Westad', u'Westad') +
    aliases(u'Layla Gauraz', u'Layla') +
    aliases(u'Lee Falk', u'Falk') +
    aliases(u'Leif Bergendorff', u'L. Bergendorff') +
    aliases(u'Lennart Allen', u'L. Allen') +
    aliases(u'Lennart Allen', u'L. Allen') + 
    aliases(u'Lennart Hartler', u'L. Hartler') +
    aliases(u'Lennart Moberg', u'L. Moberg', u'Moberg') +
    aliases(u'Marie Zackariasson', u'M. Zackariasson') +
    aliases(u'Marian J. Dern', u'Marian Dern', u'M. Dern', u'Dern') +  
    aliases(u'Mats Jönsson', u'M. Jönsson') +
    aliases(u'Mats Jönsson', u'Mats Jonsson', u'M. Jonsson') +
    aliases(u'Matt Hollingsworth', u'Hollingsworth') +  
    aliases(u'Mel Keefer', u'M. Keefer', u'Keefer') +
    aliases(u'Michael Jaatinen', u'Mikael Jaatinen', u'M. Jaatinen') +
    aliases(u'Michael Tierres', u'M. Tierres', u'Tierres') +
    aliases(u'Mikael Sol', u'Micke') +
    aliases(u'Mèziéres', u'Mézières') +
    aliases(u'Nils Schröder', u'Schröder') +
    aliases(u'Norman Worker', u'N. Worker', u'Worker', u'John Bull', u'J. Bull') +
    aliases(u'Ola Westerberg', u'O. Westerberg') +
    aliases(u'Patrik Norrman', u'Patrik Norman') +
    aliases(u'Pierre Christin', u'Christin') +
    aliases(u'PeO Carlsten', u'Peo Carlsten') +
    aliases(u'Peter Sparring', u'P. Sparring') +
    aliases(u'Robert Kanigher', u'Bob Kanigher', u'R. Kanigher') +
    aliases(u'Romano Felmang', u'R. Felmang', u'Felmang', u'Roy Mann', u'Mangiarano') +
    aliases(u'Rolf Gohs', u'Gohs') +
    aliases(u'Scott Goodall', u'S. Goodall', u'Goodall', u'Scott Godall') +
    aliases(u'Sir Arthur Conan Doyle', u'Arthur Conan Doyle', u'A. Conan Doyle', u'Sir A. Conan Doyle') +
    aliases(u'Stefan Nagy', u'S. Nagy') +
    aliases(u'Steve Ditko', u'S. Ditko') +
    aliases(u'Sverre Årnes', u'Årnes') +
    aliases(u'Sy Barry', u'Barry') +
    aliases(u'Terence Longstreet', u'Terrence Longstreet', u'T. Longstreet') +  
    aliases(u'Tina Stuve', u'T. Stuve') +  
    aliases(u'Todd Klein', u'Klein') +
    aliases(u'Tony De Paul', u'Tony DePaul', u'Tony de Paul', u'De Paul', u'DePaul') +  
    aliases(u'Tony De Zuniga', u'Tony de Zuniga') +
    aliases(u'Ulf Granberg', u'U. Granberg', u'Granberg') +
    aliases(u'Usam', u'Umberto Samarini', u'Umberto Sammarini') +
    aliases(u'Wally Wood', u'Wallace Wood') +
    aliases(u'William Vance', u'W. Vance', u'Vance') +
    aliases(u'Wilson McCoy', u'Wilson Mc Coy', u'McCoy') +
    aliases(u'Yves Sente', u'Y. Sente') +
    aliases(u'Zane Grey', u'Zane Gray', u'Zane Grej') +
    aliases(u'Özcan Eralp', u'Öscan Eralp', u'Ö. Eralp', u'Eralp')
    )

def name_alias(alias):
    if alias in ALIASES:
        return ALIASES[alias], alias
    else:
        # alias is not a known alias, hope it is a real name.
        return alias, ''
