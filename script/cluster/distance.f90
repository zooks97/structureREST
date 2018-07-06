FUNCTION average_distance(average_soap1, average_soap2, dim, d12)
    !~     Calculate distance between to averaged SOAP vectors
    !~     using the average distance kernel from De et al. (2016)
    !~     Args:
    !~         average_soap1 (numpy.ndarray): numpy array of average SOAP vector 1
    !~         average_soap2 (numpy.ndarray): numpy array of average SOAP vector 2
    !~     Returns:
    !~         float: normalized distance between average_soap1 and average_soap2
    implicit none
    integer, intent(in) :: dim
    REAL*8, intent(in), dimension(dim)  :: average_soap1, average_soap2
    REAL*8, intent(out) :: d12
    REAL*8 :: k11, k22, k12
    REAL*8 :: average_distance

    k11 = SQRT(SUM(average_soap1(:)**2))
    k22 = SQRT(SUM(average_soap2(:)**2))
    k12 = SUM(average_soap1(:) * average_soap2(:))
    average_distance = sqrt(2 - 2 * (k12 / sqrt(k11 * k22)))
END FUNCTION average_distance
FUNCTION find_free_unit()
    !--------------------------------------------------------------------------
    !
    IMPLICIT NONE
    !
    INTEGER :: find_free_unit
    INTEGER :: iunit
    LOGICAL :: opnd
    !
    !
    unit_loop: DO iunit = 99, 7, -1
       !
       INQUIRE( UNIT = iunit, OPENED = opnd )
       !
       IF ( .NOT. opnd ) THEN
          !
          find_free_unit = iunit
          !
          RETURN
          !
       END IF
       !
    END DO unit_loop
    !
    print*, 'find_free_unit()', 'free unit not found ?!?'
    CALL EXIT( 1 )
    !
    RETURN
    !
END FUNCTION find_free_unit

SUBROUTINE average_distance_matrix(vectors, filename, rowfmt, N, dim)

    !~     Generate distance matrix for a set average SOAP vectors
    !~         using the average distance kernel
    implicit none

    integer, intent(in) :: dim, N
    CHARACTER(256), intent(in)  :: filename
    CHARACTER(LEN=30), intent(in) :: rowfmt
    integer :: i, j, iun
    REAL*8, allocatable  :: distance_matrix_row(:)
    REAL*8, intent(in), dimension(N, dim)  :: vectors
    REAL*8 :: average_distance
    INTEGER :: find_free_unit
    print*, N, dim
    iun = find_free_unit()
    OPEN(UNIT=iun,FILE=filename, FORM='FORMATTED', STATUS='NEW', ACTION='WRITE')

    allocate(distance_matrix_row(N))
    DO i=1, N
        distance_matrix_row(:) = 0.0D0
        DO  j=i+1, N
            distance_matrix_row(j) = average_distance(vectors(i,:), vectors(j,:), dim)
        ENDDO
        write(iun, FMT=rowfmt), distance_matrix_row

    ENDDO
107 format (F16.8, ' ')
    close(iun)
    deallocate(distance_matrix_row)
END SUBROUTINE average_distance_matrix

