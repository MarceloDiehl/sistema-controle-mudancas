package br.jus.tjrs.ditic.mudancas.model;

/** Bolinha azul: novidade ainda não vista. {@code id} é o nome usado pela tela. */
public enum TipoAviso {
    NOVA("nova"), RETORNOU("retornou"), ATENDIMENTO("atendimento"), PARA_VALIDACAO("pendente"), STATUS("status");

    private final String id;

    TipoAviso(String id) { this.id = id; }

    public String id() { return id; }
}
