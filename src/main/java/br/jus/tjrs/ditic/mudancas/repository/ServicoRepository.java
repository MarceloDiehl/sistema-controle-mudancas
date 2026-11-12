package br.jus.tjrs.ditic.mudancas.repository;

import br.jus.tjrs.ditic.mudancas.model.Servico;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;

public interface ServicoRepository extends JpaRepository<Servico, Long> {

    /** Na ordem em que aparecem na escolha do subticket. */
    @Query("select s from Servico s join fetch s.empresa order by s.id")
    List<Servico> listarComEmpresa();

    Optional<Servico> findByEmpresaIdAndNome(Long empresaId, String nome);
}
