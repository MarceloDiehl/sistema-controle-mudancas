package br.jus.tjrs.ditic.mudancas.service;

import br.jus.tjrs.ditic.mudancas.model.Demanda;

import java.text.Normalizer;
import java.time.DateTimeException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.Locale;
import java.util.regex.Pattern;

/** Conversões e validações de formato usadas nas regras e nos textos do histórico. */
public final class Formatos {

    public static final Pattern SEI = Pattern.compile("^\\d\\.\\d{4}\\.\\d{4}/\\d{6}-\\d$");
    public static final Pattern TICKET = Pattern.compile("^\\d{8}$");
    private static final Pattern DATA_ISO = Pattern.compile("^\\d{4}-\\d{2}-\\d{2}$");
    private static final Pattern HORA = Pattern.compile("^([01]\\d|2[0-3]):[0-5]\\d$");
    private static final DateTimeFormatter BR = DateTimeFormatter.ofPattern("dd/MM/yyyy");
    private static final DateTimeFormatter HH_MM = DateTimeFormatter.ofPattern("HH:mm");
    private static final DateTimeFormatter DATA_HORA = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm");

    private Formatos() { }

    public static String br(LocalDate d) { return d == null ? "" : BR.format(d); }

    public static String hora(LocalTime t) { return t == null ? null : HH_MM.format(t); }

    public static String iso(LocalDate d) { return d == null ? null : d.toString(); }

    public static String iso(LocalDateTime d) { return d == null ? null : DATA_HORA.format(d); }

    public static String num4(Long id) { return String.format("%04d", id); }

    /** "12/11/2026 às 09:00 até 13/11/2026"; a hora é a do início, no primeiro dia. */
    public static String agendaComHora(Demanda d) {
        if (d.getDataInicio() == null) return "Sem data agendada";
        String txt = br(d.getDataInicio()) + (d.getHorario() != null ? " às " + hora(d.getHorario()) : "");
        return d.getDataFim() != null ? txt + " até " + br(d.getDataFim()) : txt;
    }

    /** Data no formato AAAA-MM-DD, de 2000 a 2100; vazio vira null. */
    public static LocalDate data(String txt) {
        if (txt == null || txt.isBlank()) return null;
        try {
            if (DATA_ISO.matcher(txt.trim()).matches()) {
                LocalDate d = LocalDate.parse(txt.trim());
                if (d.getYear() >= 2000 && d.getYear() <= 2100) return d;
            }
        } catch (DateTimeException e) {
            // cai na mensagem abaixo
        }
        throw RegraException.invalido("Data inválida. Use o formato dd/mm/aaaa ou escolha no calendário.");
    }

    /** Hora hh:mm, de 00:00 a 23:59; vazio vira null. */
    public static LocalTime hora(String txt) {
        if (txt == null || txt.isBlank()) return null;
        if (!HORA.matcher(txt.trim()).matches()) throw RegraException.invalido("Hora inválida. Use hh:mm, de 00:00 a 23:59.");
        return LocalTime.parse(txt.trim());
    }

    /** Texto aparado; vazio vira null. Recusa o que passa do limite. */
    public static String texto(String txt, int max, String campo) {
        if (txt == null) return null;
        String t = txt.strip().replaceAll("\\s+", " ");
        if (t.isEmpty()) return null;
        if (t.length() > max) throw RegraException.invalido(campo + ": até " + max + " caracteres.");
        return t;
    }

    /** Obrigatório, aparado, até o limite. */
    public static String obrigatorio(String txt, int max, String mensagem, String campo) {
        String t = texto(txt, max, campo);
        if (t == null) throw RegraException.invalido(mensagem);
        return t;
    }

    /** Sem acento e em minúsculas, para comparar nomes. */
    public static String normal(String s) {
        return Normalizer.normalize(s == null ? "" : s, Normalizer.Form.NFD).replaceAll("\\p{M}", "").toLowerCase(Locale.ROOT).trim();
    }
}
