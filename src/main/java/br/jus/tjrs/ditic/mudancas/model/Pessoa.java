package br.jus.tjrs.ditic.mudancas.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

/** Quem usa o sistema: coordenadores e técnicos. A Equipe é este cadastro. */
@Entity
@Table(name = "pessoa")
@Getter
@Setter
public class Pessoa {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 60)
    private String login;

    @Column(nullable = false, unique = true, length = 60)
    private String nome;

    @Column(name = "nome_curto", nullable = false, length = 30)
    private String nomeCurto;

    @Column(nullable = false, columnDefinition = "char(2)")
    private String iniciais;

    @Column(nullable = false, columnDefinition = "char(7)")
    private String cor;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Perfil perfil = Perfil.TECNICO;

    @Column(name = "senha_hash", length = 100)
    private String senhaHash;

    @Column(name = "deve_trocar_senha", nullable = false)
    private boolean deveTrocarSenha = true;

    @Column(name = "senha_temporaria_expira_em")
    private LocalDateTime senhaTemporariaExpiraEm;

    @Column(name = "tentativas_falhas", nullable = false)
    private short tentativasFalhas;

    @Column(name = "bloqueado_ate")
    private LocalDateTime bloqueadoAte;

    @Column(name = "ultimo_acesso")
    private LocalDateTime ultimoAcesso;

    @Column(nullable = false)
    private boolean ativo = true;

    public boolean coordenador() { return perfil == Perfil.COORDENADOR; }
}
