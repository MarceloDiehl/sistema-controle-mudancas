package br.jus.tjrs.ditic.mudancas.repository;

import br.jus.tjrs.ditic.mudancas.model.PrecoCds;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;

public interface PrecoCdsRepository extends JpaRepository<PrecoCds, Long> {

    /** Na ordem de carga (a do sistema de faturamento do DSUP), que a Configuração mantém. */
    @Query("select p from PrecoCds p join fetch p.servico order by p.id")
    List<PrecoCds> listarComServico();

    Optional<PrecoCds> findByRegiaoAndServicoId(String regiao, Long servicoId);
}
