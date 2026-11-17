package br.jus.tjrs.ditic.mudancas.repository;

import br.jus.tjrs.ditic.mudancas.model.Perfil;
import br.jus.tjrs.ditic.mudancas.model.Pessoa;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface PessoaRepository extends JpaRepository<Pessoa, Long> {

    Optional<Pessoa> findByLogin(String login);

    boolean existsByLogin(String login);

    long countByPerfilAndAtivoTrue(Perfil perfil);

    boolean existsByPerfil(Perfil perfil);

    List<Pessoa> findAllByOrderByNomeAsc();

    /** Quantos registros citam a pessoa (histórico, demandas, lixeira, decisões de acesso). Zero = pode ser apagada. */
    @Query(nativeQuery = true, value = """
            SELECT (SELECT COUNT(*) FROM historico WHERE autor_id = :id)
                 + (SELECT COUNT(*) FROM demanda WHERE tecnico_id = :id OR ticket_por_id = :id OR excluida_por_id = :id)
                 + (SELECT COUNT(*) FROM demanda_tecnico_passou WHERE tecnico_id = :id)
                 + (SELECT COUNT(*) FROM demanda_excluida WHERE excluida_por_id = :id)
                 + (SELECT COUNT(*) FROM solicitacao_acesso WHERE decidida_por = :id)""")
    long contarRegistros(@Param("id") Long id);

    /** O pedido de acesso aprovado continua registrado, sem a ligação com a conta apagada. */
    @Modifying(flushAutomatically = true, clearAutomatically = false)
    @Query(nativeQuery = true, value = "UPDATE solicitacao_acesso SET pessoa_id = NULL WHERE pessoa_id = :id")
    void soltarDasSolicitacoes(@Param("id") Long id);
}
